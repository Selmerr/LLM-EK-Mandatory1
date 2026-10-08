class Architect:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_architecture(self, requirement):
        prompt = f"""
You are the software architect for a development team.

Your job is to turn the following software requirement into a
clear technical architecture.

Requirement:
{requirement}

Produce an architecture document containing:

1. System overview
2. Component decomposition
3. Responsibilities of each component
4. Interface/API contracts
5. Data model
6. Deployment topology
7. Important technical constraints
8. Architecture decisions

Be concrete and concise.
Do not write implementation code.
"""

        return self.client.chat(
            model=self.model,
            message=prompt
        )