# Luau Code Simulator

This project is a Luau code evaluation engine with a FastAPI interface.

It is designed for educational workflows such as:
- running student code safely with runtime limits
- checking output and memory state
- simulating a small Roblox-like DataModel environment

Core stack:
- Python
- FastAPI
- ANTLR4 lexer and parser

## What It Includes

- Luau lexer and parser using ANTLR4
- AST builder and evaluator
- Built-in Roblox-like objects (for example Workspace, Part, Instance)
- FastAPI endpoints for direct execution and queued execution
- Simple static HTML client served by the API

## Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start API

```bash
uvicorn api_main:app --host 0.0.0.0 --port 8000
```

### 3. Open docs and client

- Swagger docs: http://localhost:8000/docs
- Static client page: http://localhost:8000/

Note: the app is configured with root_path /eval-api for reverse-proxy deployments.

## API Endpoints

Base app routes are defined in api_main.py.

- GET /health
	- service status, queue size, and active jobs
- POST /execute
	- execute code immediately
- POST /submit
	- enqueue a job and return job_id
- GET /result/{job_id}
	- fetch status and result for queued jobs
- GET /
	- serves example_client.html
- GET /client-config
	- returns env-driven client API base URL

## Execute Payload Example

```json
{
	"code": "local x = workspace",
	"max_run_time": 1,
	"data_model": {
		"ClassName": "DataModel",
		"Children": [
			{
				"ClassName": "Workspace",
				"Children": [
					{
						"ClassName": "Part",
						"Properties": {"Name": "Part1"}
					},
					{
						"ClassName": "Model",
						"Children": [
							{
								"ClassName": "Part"
							}
						]
					}
				]
			}
		]
	}
}
```

## Environment Variables

Current env configuration supports:

- CLIENT_API_BASE_URL
	- used by GET /client-config
	- consumed by the static client page to decide which API base URL to call
	- example value:
		- https://roblox-sim-api-production.up.railway.app/eval-api

## Docker

Build:

```bash
docker build -t luau-api .
```

Run:

```bash
docker run -p 8000:8000 luau-api
```

The container starts Gunicorn with Uvicorn workers using api_main:app.

## Testing

Run all tests from repo root:

```bash
python -m unittest discover -s test -p "*_test.py"
```

## Notes

This project is an independent implementation and is not affiliated with, endorsed by, or sponsored by Roblox Corporation.

It is intended for educational and learning purposes only.

## AI Usage Notice

The source code, documentation, and other content in this repository may not be used to train, fine-tune, evaluate, or otherwise improve artificial intelligence or machine learning models without the express written permission of the copyright holder.

All rights not expressly granted are reserved.