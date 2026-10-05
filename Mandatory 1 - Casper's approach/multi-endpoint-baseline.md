# Open WebUI Multi-Endpoint Evidence

Date: 2026-10-05

## Ollama endpoints

Endpoint 1:
- URL: http://127.0.0.1:11434
- Model: qwen3:8b

Endpoint 2:
- URL: http://127.0.0.1:11435
- Model: qwen2.5-coder:7b

## Verification

Endpoint 2 was tested using POST /api/chat.

Expected response:
ENDPOINT_2_OK

Observed:
model = qwen2.5-coder:7b
content = ENDPOINT_2_OK
done = True

HTTP server log:
POST /api/chat -> 200

## Hardware

GPU: NVIDIA GeForce RTX 5070 Ti
System RAM: approximately 32 GB
