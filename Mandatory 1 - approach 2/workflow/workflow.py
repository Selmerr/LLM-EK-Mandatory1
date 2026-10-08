from pathlib import Path
from workflow.developer_runner import run_developer

from workflow.config_loader import WorkflowConfig
from workflow.openwebui_client import OpenWebUIClient
from workflow.ticket_splitter import split_tickets

from agents.architect import Architect
from agents.tech_lead import TechLead


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHITECTURE_FILE = PROJECT_ROOT / "artifacts" / "architecture" / "architecture.md"


config = WorkflowConfig()
client = OpenWebUIClient()


# --------------------------------------------------
# Architecture
# --------------------------------------------------

architect_model = config.get_model_for_role("architect")

architect = Architect(
    client=client,
    model=architect_model
)


requirement = """
Build a simple REST API for managing books.
Users should be able to create, view, update and delete books.
"""


architecture = architect.create_architecture(requirement)


ARCHITECTURE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

ARCHITECTURE_FILE.write_text(
    architecture,
    encoding="utf-8"
)


print("\n===== ARCHITECTURE =====\n")
print(architecture)

print(
    f"\nArchitecture saved to: {ARCHITECTURE_FILE}"
)


# --------------------------------------------------
# Tech Lead
# --------------------------------------------------

tech_lead_model = config.get_model_for_role("tech_lead")

tech_lead = TechLead(
    client=client,
    model=tech_lead_model
)


tickets = tech_lead.create_tickets(
    architecture
)


TICKETS_FILE = PROJECT_ROOT / "artifacts" / "tickets.md"

TICKETS_FILE.write_text(
    tickets,
    encoding="utf-8"
)

# --------------------------------------------------
# Developer ticket allocation
# --------------------------------------------------

developer_a_tickets, developer_b_tickets = split_tickets(
    tickets
)

print("\n===== DEVELOPER A TICKETS =====\n")

for ticket in developer_a_tickets:
    print(ticket)

print("\n===== DEVELOPER B TICKETS =====\n")

for ticket in developer_b_tickets:
    print(ticket)
    
# --------------------------------------------------
# Developer A
# --------------------------------------------------

developer_a_model = config.get_model_for_role(
    "developer_a"
)

if developer_a_tickets:
    developer_a_result = run_developer(
        client=client,
        model=developer_a_model,
        ticket=developer_a_tickets[0],
        branch_name="developer-a",
        repo_path=PROJECT_ROOT / "demo_repo"
    )