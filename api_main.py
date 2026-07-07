from __future__ import annotations

from fastapi import FastAPI , HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
import asyncio
from contextlib import asynccontextmanager
from main import run
import typing
import uuid
import time
import os
import dotenv
from post_evaluation.state_processor import process_memory

dotenv.load_dotenv()

CLIENT_API_BASE_URL = os.getenv(
    "CLIENT_API_BASE_URL",
    "https://roblox-sim-api-production.up.railway.app/eval-api"
).rstrip("/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = [asyncio.create_task(worker()) for _ in range(2)]
    app.state.workers = tasks
    yield
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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


# Response Models
class ExecutionResponse(BaseModel):
    status: str = Field(..., description="Execution status: done, failed_to_parse, failed_to_build_ast, failed_syntax, failed_runtime, failed_timeout, failed_generic, failed_datamodel")
    output: typing.List[str] = Field(default=[], description="Output from print statements")
    memory: typing.Dict[str, typing.Any] = Field(default={}, description="Final state of variables")
    error: typing.Optional[str] = Field(None, description="Error message if execution failed")


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
    print(data_model_dict)
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
                    data_model_dict = job.datamodel.model_dump(mode="python", exclude_none=True)
                except Exception as e:
                    job_results[job.job_id] = {
                        "status": "failed_datamodel",
                        "error": f"Invalid datamodel: {str(e)}",
                        "created_at": job.created_at
                    }
                    return
            
            result = await asyncio.wait_for(
                execute_code_internal(job.code, data_model_dict, 0.1),
                timeout=0.2 
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

@app.get("/")
def client_page():
    return FileResponse("example_client.html")


@app.get("/client-config")
def client_config():
    return {
        "api_base_url": CLIENT_API_BASE_URL
    }

@app.get("/health")
def health_check():
    """Check API health and service status."""
    return {
        "status": "healthy",
        "service": "Lua Evaluation API",
        "version": "1.0.0",
        "queue_size": job_queue.qsize(),
        "active_jobs": len(job_results)
    } , 200


@app.post("/execute", response_model=ExecutionResponse, status_code=200)
async def execute_code(request: CodeRequest):
    """Execute Lua code directly and return results immediately.
    """
    try:
        data_model_dict = None
        if request.data_model:
            try:
                data_model_dict = request.data_model.model_dump(mode="python", exclude_none=True)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid datamodel: {str(e)}"
                )
        
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

