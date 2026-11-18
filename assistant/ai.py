"""Optional OpenAI-powered conversational brain."""
import os
from openai import OpenAI


class AIBrain:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def available(self) -> bool:
        return self.client is not None

    def ask(self, prompt: str, history: list[dict] | None = None) -> str:
        if not self.client:
            return "AI is not configured yet. Add your OpenAI API key in the .env file."
        messages = [{
            "role": "system",
            "content": (
                "You are the user's helpful desktop voice assistant. "
                "Keep answers clear, concise, friendly, and suitable for being spoken aloud. "
                "The user is on macOS."
            ),
        }]
        messages.extend((history or [])[-8:])
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.6
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            print(f"AI request failed: {exc}")
            return "I could not reach the AI service. Please check your API key and internet connection."
