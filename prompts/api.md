Write docs/openapi.yaml as a valid OpenAPI 3.0 specification.

Required endpoints:
- GET /notes
- POST /notes
- DELETE /notes/{id}

Rules:
- GET and POST must both be under the single /notes path.
- DELETE must be under /notes/{id}.
- The id path parameter must include required: true.
- POST must use requestBody, not an OpenAPI 2 "in: body" parameter.
- Do not duplicate YAML keys.
- Include appropriate response codes.
- Output only docs/openapi.yaml.
- Keep it under 80 lines.