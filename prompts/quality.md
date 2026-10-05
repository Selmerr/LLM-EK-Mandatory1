You are the quality reporting worker.

Read:
- artifacts/pytest.txt

Create:
- docs/quality.md

Produce a concise quality report.

Include:

# Quality Report

## Test Results
- total tests
- passed tests
- failed tests
- failed test names
- concise cause of failures

Use the final pytest summary exactly.
Do not invent counts.

## Static Validation
report the OpenAPI validation result from artifacts/openapi.txt, and state that no Python lint or type checking was run, because linting is out of scope for this project.

## Known Limitations and Risks
- summarize limitations revealed by the test results

Do not modify source code or tests.
Do not attempt to fix anything.
Keep the report concise.