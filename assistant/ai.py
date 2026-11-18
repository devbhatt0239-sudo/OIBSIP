
import requests


class AIBrain:
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.model = "qwen2.5:3b"

    @property
    def available(self):
        try:
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=3
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def ask(self, prompt, history=None):
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful desktop voice assistant. "
                    "Give clear, friendly and concise answers. "
                    "The user is using a MacBook."
                )
            }
        ]

        messages.extend((history or [])[-8:])
        messages.append({"role": "user", "content": prompt})

        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()

            return response.json()["message"]["content"].strip()

        except requests.RequestException as exc:
            print("Ollama error:", exc)
            return "Sorry, I could not connect to my local AI model."
