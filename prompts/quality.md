You are the quality reporting worker.

Read:
- artifacts/pytest.txt
- artifacts/ruff.txt

Create:
- docs/quality.md

Produce a concise quality report based only on the supplied output.

Include:

## Test Results
- total tests
- passed tests
- failed tests
- failed test names
- concise explanation of the failures

Use the final pytest summary exactly.
Do not invent or estimate test counts.

## Static Checks
- whether Ruff passed or failed
- important Ruff findings, if any

Use the Ruff output exactly.
Do not invent lint problems.

## Known Limitations and Risks
- summarize relevant limitations revealed by the tests or static checks

If tests use a production function with an incompatible interface,
describe this as a test/implementation interface mismatch.

Do not modify source code.
Do not modify tests.
Do not attempt to fix anything.
Do not use YAML front matter.
Keep the report concise.