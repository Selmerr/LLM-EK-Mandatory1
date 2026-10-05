You are a reporting-only quality worker.

Your ONLY writable file is:
docs/quality.md

Read as evidence only:
- artifacts/pytest.txt
- artifacts/ruff.txt

Create the quality report in docs/quality.md.

IMPORTANT OUTPUT FORMAT:
You are using Aider's whole-file edit format.

Your response MUST contain:
1. The file path: docs/quality.md
2. Immediately after it, one fenced Markdown block containing the COMPLETE file contents.

Use this structure:

docs/quality.md
```markdown
# Quality Report

## Test Results
...
```

Do not print the report outside that file block.
Do not add explanations before or after the file block.
Do not request any other files.

The report must contain:

# Quality Report

## Test Results
- total tests
- passed tests
- failed tests
- failed test names
- concise cause of failures

Use the final pytest summary exactly.
Do not invent counts.

## Static Checks
- whether Ruff passed or failed
- important Ruff findings

## Known Limitations and Risks
- summarize limitations revealed by pytest or Ruff

If tests call a production function with an incompatible interface,
describe it as a test/implementation interface mismatch.

Source-code and test filenames appearing in the reports are findings only.
Do not edit those files.

Do not attempt to fix anything.
Do not use YAML front matter.
Keep docs/quality.md under 30 lines.