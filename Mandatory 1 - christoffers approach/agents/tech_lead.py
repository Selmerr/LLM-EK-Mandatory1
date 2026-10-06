class TechLead:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_tickets(self, architecture):
        prompt = f"""
You are the technical lead for a software development team.

You must turn the architecture document below into implementation tickets.

IMPORTANT RULES:

1. Treat the architecture document as the single source of truth.
2. Do NOT invent requirements, constraints, components, limits,
   technologies, endpoints, or business rules that are not present
   in the architecture.
3. Do NOT change any values from the architecture.
   For example, if the architecture says a year is 1800-2100,
   the tickets must also say 1800-2100.
4. If the architecture contains a contradiction or ambiguity,
   explicitly flag it instead of silently changing the requirement.
5. Do not add requirements merely because they are common practice.
6. Do not implement anything.
7. Keep the output reasonably concise.

ARCHITECTURE DOCUMENT
=====================

{architecture}

=====================

Create incremental development tickets.

Each ticket must contain:

## Ticket ID
Use TKT-001, TKT-002, etc.

## Title

## Objective

## Scope

## Out of Scope

## Dependencies

## Acceptance Criteria

Acceptance criteria must be concrete and testable.

## Definition of Done

The tickets must:

- Cover the components and responsibilities in the architecture.
- Be ordered according to dependencies.
- Have clear scope boundaries.
- Avoid overlapping responsibilities.
- Preserve the exact requirements from the architecture.

At the end, provide a short section called:

## Architecture Issues

List any contradictions, ambiguities, or missing information you detected.

Do not invent solutions for those issues.
"""

        return self.client.chat(
            model=self.model,
            message=prompt
        )