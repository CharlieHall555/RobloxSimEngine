# Lua Evaluation API

A production-ready FastAPI service for executing and evaluating Lua code in an educational context.

## Features

- ✅ **Execute Lua code** with custom datamodels
- ✅ **Evaluate code** against learning objectives
- ✅ **Async job queue** for long-running tasks
- ✅ **Timeout protection** to prevent infinite loops
- ✅ **Comprehensive error handling** with detailed status codes
- ✅ **CORS enabled** for frontend integration
- ✅ **Type-safe API** with Pydantic models
- ✅ **Docker ready** for easy deployment

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
uvicorn api_main:app --host 0.0.0.0 --port 8080 --reload
```

### Run with Docker

```bash
docker build -t lua-eval-api .
docker run -p 8080:8080 lua-eval-api
```

## API Endpoints

### Health Check

**GET** `/health`

Check API health and status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Lua Evaluation API",
  "version": "1.0.0",
  "queue_size": 0,
  "active_jobs": 5
}
```

---

### Execute Code (Direct)

**POST** `/execute`

Execute Lua code immediately and get results synchronously. Best for interactive, quick executions.

**Request:**
```json
{
  "code": "local x = 5\nprint(x * 2)",
  "max_run_time": 0.1,
  "data_model": {
    "ClassName": "DataModel",
    "Children": [
      {
        "ClassName": "Workspace",
        "Children": []
      }
    ]
  }
}
```

**Response:**
```json
{
  "status": "done",
  "output": ["10"],
  "memory": {
    "x": 5
  },
  "error": null
}
```

**Status Codes:**
- `done` - Execution successful
- `failed_to_parse` - Syntax error in Lua code
- `failed_to_build_ast` - AST construction failed
- `failed_syntax` - Syntax error
- `failed_runtime` - Runtime error during execution
- `failed_timeout` - Execution exceeded time limit
- `failed_generic` - Generic error
- `failed_datamodel` - Invalid datamodel

---

### Execute and Evaluate (Combined)

**POST** `/execute-and-evaluate`

Execute code and evaluate it against objectives in a single request. Most commonly used endpoint for educational assessments.

**Request:**
```json
{
  "code": "local x = 10\nlocal y = 20\nprint(\"Sum: \" .. (x + y))",
  "max_run_time": 0.1,
  "objective": {
    "expected_output": ["Sum: 30"],
    "expected_state": {
      "x": 10,
      "y": 20
    }
  }
}
```

**Response:**
```json
{
  "status": "done",
  "passed": true,
  "message": "All objectives met!",
  "output": ["Sum: 30"],
  "memory": {
    "x": 10,
    "y": 20
  }
}
```

---

### Submit Job (Async)

**POST** `/submit`

Queue a code execution job for asynchronous processing. Use for long-running code or when polling for results.

**Request:**
```json
{
  "code": "for i=1,10 do print(i) end",
  "max_run_time": 0.5
}
```

**Response:**
```json
{
  "status": "queued",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Get Job Result

**GET** `/result/{job_id}`

Retrieve the result of a queued job.

**Response (Pending):**
```json
{
  "status": "pending",
  "output": null,
  "memory": null,
  "error": null
}
```

**Response (Success):**
```json
{
  "status": "done",
  "output": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  "memory": {
    "i": 10
  },
  "error": null
}
```

---

### Evaluate Job

**POST** `/evaluate/{job_id}`

Evaluate a completed job against objectives.

**Request:**
```json
{
  "expected_output": ["1", "2", "3"],
  "expected_state": {
    "i": 3
  }
}
```

**Response:**
```json
{
  "status": "done",
  "passed": false,
  "message": "Expected output mismatch at index 3",
  "output": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  "memory": {
    "i": 10
  }
}
```

---

## Data Models

### Datamodel Structure

Datamodels represent Roblox-like object hierarchies:

```json
{
  "ClassName": "DataModel",
  "Name": "Game",
  "Properties": {},
  "Children": [
    {
      "ClassName": "Workspace",
      "Name": "Workspace",
      "Children": [
        {
          "ClassName": "Part",
          "Name": "MyPart",
          "Properties": {
            "Position": [0, 5, 0],
            "Size": [4, 1, 2]
          }
        }
      ]
    }
  ]
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid code/datamodel)
- `404` - Resource not found (invalid job_id)
- `500` - Internal server error

Error responses include detailed messages:

```json
{
  "status": "failed_runtime",
  "error": "attempt to perform arithmetic on a nil value",
  "output": [],
  "memory": {}
}
```

## Rate Limiting & Timeouts

- **Default execution timeout**: 0.1 seconds
- **Maximum execution timeout**: 5.0 seconds
- **Job retention**: 100 seconds
- **Worker threads**: 2 concurrent workers

## Development

### Running Tests

```bash
# Run all tests
python -m pytest test/

# Run specific test module
python -m pytest test/evaluation/eval_if_test.py
```

### Project Structure

```
├── api_main.py           # FastAPI application
├── main.py               # Core execution engine
├── classes/              # Lua and Roblox class implementations
├── evaluation/           # Code evaluation engine
├── parser/               # ANTLR Lua parser
├── syntax_tree/          # AST builder and nodes
├── post_evaluation/      # Objective evaluation
├── functions/            # Built-in Lua functions
└── test/                 # Test suites
```

## API Documentation

Once running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8080/eval-api/docs
- **ReDoc**: http://localhost:8080/eval-api/redoc

## License

Proprietary - Blox Code Academy