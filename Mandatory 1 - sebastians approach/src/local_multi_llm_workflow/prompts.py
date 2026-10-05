SYSTEM_PROMPT = """You are a local software-engineering agent.
Return concise, actionable output.
Write durable artifacts rather than relying on hidden chat history.
Return final output only. Do not include hidden reasoning, chain-of-thought, thinking traces, or analysis prose.
If previous artifacts are provided as context, do not recreate them. Produce only the current role's requested artifact."""


def role_prompt(role: str, goal: str, repo_tree: str, context: str) -> str:
    return f"""Role: {role}

Goal:
{goal}

Repository tree:
{repo_tree}

Context:
{context}

Produce only the artifact requested for this role.
Keep the answer under 500 words unless a structured spec requires more.
Use Markdown unless told otherwise."""


def implementation_prompt(worker: str, goal: str, repo_tree: str, context: str, task: str, target_root: str) -> str:
    return f"""Role: {worker}

Goal:
{goal}

Repository tree:
{repo_tree}

Context:
{context}

Implementation assignment from the generated backlog:
{task}

Target repository path:
{target_root}/

Return actual project files using this exact format:
BEGIN_FILE {target_root}/path/to/file.ext
file content here
END_FILE

You are allowed to create any directories needed inside {target_root}/ by using nested file paths.
Do not avoid nested folders. Do not ask permission in your answer. The workflow will ask the user before creating folders or applying file changes.
Every file path must be under {target_root}/.
Create actual runnable project files required by your backlog assignment.
If your files require package manifests, run scripts, entrypoints, HTML bootstraps, environment examples, or config files to launch or test them, include those files too unless another ticket clearly owns them.
Do not create architecture-only files unless the backlog explicitly assigns them as implementation deliverables.
Return only BEGIN_FILE blocks. Do not return descriptions, diffs, markdown explanations, or fenced code blocks outside BEGIN_FILE blocks."""


def file_creation_prompt(role: str, goal: str, repo_tree: str, context: str, target_root: str, task: str) -> str:
    return f"""Role: {role}

Goal:
{goal}

Repository tree:
{repo_tree}

Context:
{context}

Task:
{task}

Create actual files using this exact format:
BEGIN_FILE {target_root}/path/to/file.ext
file content here
END_FILE

All file paths must be under {target_root}/.
You may create folders by using nested file paths.
The workflow will ask the user before applying your generated files.
If commands should be run after files are written, add them as separate lines:
COMMAND: command to run

Commands will be run with the working directory already set to {target_root}/.
Do not prefix commands with cd {target_root}, cd ./{target_root}, or cd .\\{target_root}.
Return only BEGIN_FILE blocks and optional COMMAND lines."""
