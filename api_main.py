from __future__ import annotations

from fastapi import FastAPI , HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
import json
import asyncio
from contextlib import asynccontextmanager
from main import run  # Your actual code runner
import typing
import uuid
import time
import os
from post_evaluation.Objective_Evaluation import eval_expected_memory , eval_expected_output
from post_evaluation.Objective import Objective
import dotenv
from post_evaluation.state_processor import process_memory
from evaluation.DataModelGenerator import generate_data_model , Instance

dotenv.load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # -- startup phase --
    tasks = [asyncio.create_task(worker()) for _ in range(2)]
    app.state.workers = tasks
    yield
    # -- shutdown phase --
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(
    root_path="/eval-api",
    lifespan=lifespan,
    title="Lua Evaluation API",
    description="Execute and evaluate Lua code with educational objectives",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_queue: asyncio.Queue = asyncio.Queue()
job_counter = 0
job_results: typing.Dict = {}

# -------------------------------
# API_CLASSES
# -------------------------------

class RequestDatamodel(BaseModel):
    Name: str = Field(default="DataModel", description="Name of the instance")
    ClassName: str = Field(..., description="Class name of the instance")
    Properties: typing.Optional[typing.Dict[str, typing.Any]] = Field(None, description="Properties to set on the instance")
    Children: typing.Optional[typing.List["RequestDatamodel"]] = Field(None, description="Child instances")

    class Config:
        schema_extra = {
            "example": {
                "Name": "MyModel",
                "ClassName": "Model",
                "Properties": {"Archivable": True},
                "Children": [
                    {
                        "Name": "Part1",
                        "ClassName": "Part",
                        "Properties": {"Position": [0,0,0]},
                        "Children": []
                    }
                ]
            }
        }


class CodeRequest(BaseModel):
    code: str = Field(..., description="Lua code to execute", min_length=1)
    data_model: typing.Optional[RequestDatamodel] = Field(None, description="Optional datamodel for execution context")
    max_run_time: float = Field(0.1, description="Maximum execution time in seconds", gt=0, le=5.0)


class ObjectiveRequest(BaseModel):
    expected_output: typing.List[str] = Field(default=[], description="Expected output lines or tags")
    expected_state: typing.Dict[str, typing.Union[str, int, float]] = Field(default={}, description="Expected variable states")


class ExecuteAndEvaluateRequest(BaseModel):
    code: str = Field(..., description="Lua code to execute", min_length=1)
    data_model: typing.Optional[RequestDatamodel] = Field(None, description="Optional datamodel for execution context")
    max_run_time: float = Field(0.1, description="Maximum execution time in seconds", gt=0, le=5.0)
    objective: ObjectiveRequest = Field(..., description="Evaluation objectives")


# Response Models
class ExecutionResponse(BaseModel):
    status: str = Field(..., description="Execution status: done, failed_to_parse, failed_to_build_ast, failed_syntax, failed_runtime, failed_timeout, failed_generic, failed_datamodel")
    output: typing.List[str] = Field(default=[], description="Output from print statements")
    memory: typing.Dict[str, typing.Any] = Field(default={}, description="Final state of variables")
    error: typing.Optional[str] = Field(None, description="Error message if execution failed")


class EvaluationResponse(BaseModel):
    status: str = Field(..., description="Execution status")
    passed: bool = Field(..., description="Whether all objectives were met")
    message: typing.Optional[str] = Field(None, description="Evaluation feedback message")
    output: typing.List[str] = Field(default=[], description="Actual output from execution")
    memory: typing.Dict[str, typing.Any] = Field(default={}, description="Actual final state")


class JobResponse(BaseModel):
    status: str = Field(..., description="Job queue status")
    job_id: str = Field(..., description="Unique job identifier")


class JobStatusResponse(BaseModel):
    status: str = Field(..., description="Job execution status")
    output: typing.Optional[typing.List[str]] = Field(default=None, description="Output if completed")
    memory: typing.Optional[typing.Dict[str, typing.Any]] = Field(default=None, description="Memory state if completed")
    error: typing.Optional[str] = Field(default=None, description="Error message if failed")

# -------------------------------
# JOB & WORKER SETUP
# -------------------------------

class Job:
    code : str
    job_id : str
    datamodel : typing.Optional[RequestDatamodel]
    created_at : float
    def __init__(self, code: str  , datamodel : typing.Optional[RequestDatamodel], lesson_id:str=""):
        self.job_id = str(uuid.uuid4())
        self.code = code
        self.datamodel = datamodel
        self.created_at = time.time()


async def execute_code_internal(code: str, data_model_dict: typing.Optional[dict] = None, max_run_time: float = 0.1) -> typing.Tuple[bool, str, typing.Any]:
    """Internal function to execute code synchronously."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, run, code, data_model_dict, False, max_run_time)


def extract_top_frame(processed_memory: list) -> dict:
    """Extract the top stack frame from processed memory list."""
    if processed_memory and len(processed_memory) > 0:
        return processed_memory[-1]  # Return the top/last frame
    return {}


async def process_job(job: Job):
    print(f"[Worker] Processing job {job.job_id}")
    try:
        job_results[job.job_id] = {"status": "pending" , "created_at" : job.created_at}
        
        try:
            data_model_dict = None
            if job.datamodel:
                try:
                    data_model_dict = job.datamodel.model_dump(mode="python")
                except Exception as e:
                    job_results[job.job_id] = {
                        "status": "failed_datamodel",
                        "error": f"Invalid datamodel: {str(e)}",
                        "created_at": job.created_at
                    }
                    return
            
            result = await asyncio.wait_for(
                execute_code_internal(job.code, data_model_dict, 0.1),
                timeout=0.2  # Slightly longer than max_run_time
            )

            result_success = result[0]
            result_status = result[1]
            result_state = result[2]
           
            processed_state = process_memory(result_state.memory)
            top_frame = extract_top_frame(processed_state)

            job_results[job.job_id] = {
                "status": result_status,
                "output": result_state.output,
                "memory": top_frame,
                "created_at": job.created_at,
                "success": result_success
            }

            print(f"[Worker] Job {job.job_id} completed: {result_status}")
        except asyncio.TimeoutError:
            job_results[job.job_id] = {
                "status": "failed_timeout",
                "error": "Execution exceeded maximum time limit",
                "created_at": job.created_at
            }
        except Exception as e:
            job_results[job.job_id] = {
                "status": "failed",
                "error": str(e),
                "created_at": job.created_at
            }
    except Exception as e:
        job_results[job.job_id] = {
            "status": "failed",
            "error": str(e),
            "created_at": job.created_at
        }


async def worker():
    while True:
        job = await job_queue.get()
        try:
            await process_job(job)
        finally:
            job_queue.task_done()

async def job_cleanup():
    while True:
        await asyncio.sleep(10)  # Run eve+ry 10 seconds
        now = time.time()
        to_delete = [
            job_id for job_id, result in job_results.items()
            if now - result.get("created_at", 0) > 100
        ]

        amount_deleted = len(to_delete)
        for job_id in to_delete:
            del job_results[job_id]
        print(f"[Cleanup] Removed {amount_deleted} expired jobs")


# -------------------------------
# API ENDPOINTS
# -------------------------------

@app.get("/health")
def health_check():
    """Check API health and service status."""
    return {
        "status": "healthy",
        "service": "Lua Evaluation API",
        "version": "1.0.0",
        "queue_size": job_queue.qsize(),
        "active_jobs": len(job_results)
    }


@app.post("/execute", response_model=ExecutionResponse, status_code=200)
async def execute_code(request: CodeRequest):
    """Execute Lua code directly and return results immediately.
    
    This endpoint executes code synchronously without using the job queue.
    Use this for quick, interactive code execution.
    """
    try:
        data_model_dict = None
        if request.data_model:
            try:
                data_model_dict = request.data_model.model_dump(mode="python")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid datamodel: {str(e)}"
                )
        
        # Execute code
        result = await execute_code_internal(request.code, data_model_dict, request.max_run_time)
        
        result_success = result[0]
        result_status = result[1]
        result_state = result[2]
        
        processed_state = process_memory(result_state.memory)
        top_frame = extract_top_frame(processed_state)
        
        return ExecutionResponse(
            status=result_status,
            output=result_state.output,
            memory=top_frame,
            error=None if result_success else result_status
        )
        
    except asyncio.TimeoutError:
        return ExecutionResponse(
            status="failed_timeout",
            output=[],
            memory={},
            error="Execution exceeded maximum time limit"
        )
    except Exception as e:
        return ExecutionResponse(
            status="failed_generic",
            output=[],
            memory={},
            error=str(e)
        )


@app.post("/execute-and-evaluate", response_model=EvaluationResponse, status_code=200)
async def execute_and_evaluate(request: ExecuteAndEvaluateRequest):
    """Execute Lua code and evaluate it against objectives in a single request.
    
    This combines execution and evaluation for convenience and performance.
    """
    try:
        # Execute code
        data_model_dict = None
        if request.data_model:
            try:
                data_model_dict = request.data_model.model_dump(mode="python")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid datamodel: {str(e)}"
                )
        
        result = await execute_code_internal(request.code, data_model_dict, request.max_run_time)
        
        result_success = result[0]
        result_status = result[1]
        result_state = result[2]
        
        # If execution failed, return early
        if not result_success:
            return EvaluationResponse(
                status=result_status,
                passed=False,
                message=f"Execution failed: {result_status}",
                output=result_state.output,
                memory=extract_top_frame(process_memory(result_state.memory))
            )
        
        processed_state = process_memory(result_state.memory)
        top_frame = extract_top_frame(processed_state)
        
        # Evaluate against objectives
        objective = Objective(
            request.objective.expected_output,
            request.objective.expected_state
        )
        
        # Check output
        passed_out, out_msg = eval_expected_output(result_state.output, objective.output_tags)
        if not passed_out:
            return EvaluationResponse(
                status=result_status,
                passed=False,
                message=out_msg,
                output=result_state.output,
                memory=top_frame
            )
        
        # Check state (pass full stack to eval_expected_memory)
        passed_mem, mem_msg = eval_expected_memory(processed_state, objective.state_variables)
        if not passed_mem:
            return EvaluationResponse(
                status=result_status,
                passed=False,
                message=mem_msg,
                output=result_state.output,
                memory=top_frame
            )
        
        return EvaluationResponse(
            status=result_status,
            passed=True,
            message="All objectives met!",
            output=result_state.output,
            memory=top_frame
        )
        
    except asyncio.TimeoutError:
        return EvaluationResponse(
            status="failed_timeout",
            passed=False,
            message="Execution exceeded maximum time limit",
            output=[],
            memory={}
        )
    except Exception as e:
        return EvaluationResponse(
            status="failed_generic",
            passed=False,
            message=f"Error: {str(e)}",
            output=[],
            memory={}
        )


@app.post("/submit", response_model=JobResponse, status_code=200)
async def submit_code(request: CodeRequest):
    """Queue code execution job for asynchronous processing.
    
    Use this for longer-running code or when you want to poll for results.
    Check status with GET /result/{job_id}
    """
    job = Job(code=request.code, datamodel=request.data_model)
    await job_queue.put(job)
    return JobResponse(status="queued", job_id=job.job_id)


@app.get("/result/{job_id}", response_model=JobStatusResponse)
async def get_result(job_id: str):
    """Retrieve job execution result by job ID.
    
    Returns the current status and results if available.
    """
    result = job_results.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found or expired")

    status = result.get("status", "pending")
    
    if status == "pending":
        return JobStatusResponse(status="pending", output=None, memory=None, error=None)
    
    # Check for failures
    if "failed" in status or status == "timeout":
        return JobStatusResponse(
            status=status,
            output=None,
            memory=None,
            error=result.get("error", "Unknown error")
        )
    
    # Success case
    return JobStatusResponse(
        status=status,
        output=result.get("output", []),
        memory=result.get("memory", {}),
        error=None
    )


@app.post("/evaluate/{job_id}", response_model=EvaluationResponse)
async def evaluate_job(job_id: str, objective: ObjectiveRequest = Body(...)):
    """Evaluate a completed job against objectives.
    
    The job must have completed successfully before evaluation.
    """
    result = job_results.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found or expired")

    status = result.get("status", "pending")
    
    if status == "pending":
        raise HTTPException(status_code=400, detail="Job is still pending")
    
    if "failed" in status or status == "timeout":
        return EvaluationResponse(
            status=status,
            passed=False,
            message=f"Execution failed: {result.get('error', status)}",
            output=[],
            memory={}
        )

    memory = result.get("memory", {})
    output = result.get("output", [])
    
    # Create objective and evaluate
    given_objective = Objective(objective.expected_output, objective.expected_state)
    
    # Check output
    passed_out, out_msg = eval_expected_output(output, given_objective.output_tags)
    if not passed_out:
        return EvaluationResponse(
            status=status,
            passed=False,
            message=out_msg,
            output=output,
            memory=memory
        )
    
    # Check state (memory from job_results is already the top frame as a dict,
    # but eval_expected_memory expects a List[Dict], so wrap it)
    memory_stack = [memory] if memory else [{}]
    passed_mem, mem_msg = eval_expected_memory(memory_stack, given_objective.state_variables)
    if not passed_mem:
        return EvaluationResponse(
            status=status,
            passed=False,
            message=mem_msg,
            output=output,
            memory=memory
        )
    
    return EvaluationResponse(
        status=status,
        passed=True,
        message="All objectives met!",
        output=output,
        memory=memory
    )

