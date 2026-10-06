class Developer:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_implementation_plan(self, ticket):
        prompt = f"""
You are a software developer working on a development team.

You have been assigned the following ticket:

--- TICKET START ---
{ticket}
--- TICKET END ---

Create a concise implementation plan.

The plan must contain:

1. Files that need to be created or modified
2. Changes required in each file
3. Tests that should be added or changed
4. Any dependencies on other tickets

Rules:

- Only work within the scope of the ticket.
- Do not implement the code.
- Do not invent additional features.
- Do not modify unrelated files.
- If information is missing, clearly identify it.

Return the implementation plan as Markdown.
"""

        return self.client.chat(
            model=self.model,
            message=prompt
        )

    def create_code_changes(self, ticket, implementation_plan):
        prompt = f"""
You are a software developer implementing a specific ticket.

TICKET:
{ticket}

IMPLEMENTATION PLAN:
{implementation_plan}

Return the required code changes as a list of files.

For every file, use this format:

FILE: path/to/file
CONTENT:
<complete file contents>
END FILE

Rules:

- Only modify files required by the ticket.
- Do not modify unrelated files.
- Do not add features outside the ticket.
- Provide complete file contents, not patches.
- Do not include explanations outside the FILE sections.
- If a new file is required, provide its complete contents.
"""

        return self.client.chat(
            model=self.model,
            message=prompt
        )