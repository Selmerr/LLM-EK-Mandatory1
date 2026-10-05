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
- State that the OpenAPI specification is validated separately by the workflow.
- State that no additional Python lint or type checking is configured.

## Known Limitations and Risks
- summarize limitations revealed by the test results

If tests call production functions using an incompatible interface,
describe this as a test/implementation interface mismatch.

Do not modify source code or tests.
Do not attempt to fix anything.
Keep the report concise.