Read the final pytest summary literally.

Do not calculate or infer test counts.
Copy the total, passed, and failed counts directly from the pytest output.

For example, if pytest says:
"3 failed, 5 passed"
then report exactly:
Total: 8
Passed: 5
Failed: 3

Do not classify a failure as an implementation defect unless the traceback
shows production code is incorrect.
If the test calls a function with arguments that the function does not accept,
describe this as a test/implementation interface mismatch.