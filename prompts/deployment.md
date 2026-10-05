You are the deployment worker.

Read:
- pyproject.toml
- uv.lock
- src/llm_man_1/api.py
- docs/architecture.md

Create:
- Dockerfile

Create a simple Docker image for the Notes Flask application.

Requirements:
- Use Python 3.12 slim.
- Install uv.
- Copy pyproject.toml and uv.lock.
- Install the project dependencies using uv.
- Copy the application source code.
- Expose port 5000.
- Start the Flask application on 0.0.0.0:5000.
- Use llm_man_1.api as the Flask application.
- Keep the image simple and suitable for local validation.

Only modify Dockerfile.
Do not modify application code, tests, or documentation.