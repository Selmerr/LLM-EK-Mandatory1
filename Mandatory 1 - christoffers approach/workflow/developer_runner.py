from agents.developer import Developer
from workflow.code_change_parser import parse_code_changes
from workflow.developer_workspace import DeveloperWorkspace
from workflow.approval import request_approval


def run_developer(
    client,
    model,
    ticket,
    branch_name,
    repo_path
):
    developer = Developer(
        client=client,
        model=model
    )

    workspace = DeveloperWorkspace(repo_path)

    # Prepare the correct Git branch
    workspace.prepare(branch_name)

    print(f"\n===== {branch_name.upper()} =====")
    print(f"Working on branch: {branch_name}")

    # Ask the LLM for an implementation plan
    plan = developer.create_implementation_plan(ticket)

    print("\n===== IMPLEMENTATION PLAN =====\n")
    print(plan)

    # Ask the LLM for proposed code changes
    response = developer.create_code_changes(
        ticket=ticket,
        implementation_plan=plan
    )

    # Convert the response into structured file changes
    changes = parse_code_changes(response)

    if not changes:
        raise ValueError(
            "Developer returned no parseable code changes."
        )

    # Human approval before modifying files
    approved = request_approval(changes)

    if not approved:
        print("Changes rejected.")
        return {
            "approved": False,
            "branch": branch_name,
            "plan": plan,
            "changes": changes,
            "diff": ""
        }

    # Apply the approved changes
    workspace.apply_changes(changes)

    # Show the resulting Git diff
    diff = workspace.get_diff()

    print("\n===== GIT DIFF =====\n")
    print(diff)

    return {
        "approved": True,
        "branch": branch_name,
        "plan": plan,
        "changes": changes,
        "diff": diff
    }