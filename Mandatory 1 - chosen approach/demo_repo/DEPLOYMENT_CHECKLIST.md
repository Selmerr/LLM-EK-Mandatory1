# Deployment Validation Checklist

## Required Checks

- [ ] Application dependencies can be installed from committed manifest files.
- [ ] Automated tests pass locally or in CI.
- [ ] Runtime configuration is documented with safe example values.
- [ ] The application has a clear start command.
- [ ] Generated source, tests, documentation, and deployment files are committed together.

## Local Validation

Run the generated project's documented setup and test commands before deployment. If the project contains a Node.js `package.json`, run `npm install` and `npm test` from the folder that contains it. If the project contains a Python `pyproject.toml`, install the project dependencies and run the documented test command.

## Notes

This checklist is created by the workflow so every run has a deployability artifact even when the model-generated deployment validator produces incomplete output.
