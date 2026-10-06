import os

import requests
from dotenv import load_dotenv


load_dotenv()


class OpenWebUIClient:

    def __init__(self):
        self.base_url = os.getenv("OPENWEBUI_BASE_URL")
        self.api_key = os.getenv("OPENWEBUI_API_KEY")

        if not self.base_url:
            raise ValueError("OPENWEBUI_BASE_URL is not set")

        if not self.api_key:
            raise ValueError("OPENWEBUI_API_KEY is not set")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, model, message):
        url = f"{self.base_url}/api/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": message,
                }
            ],
            "stream": False,
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]