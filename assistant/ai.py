"""Free local AI brain powered by Ollama."""
import requests


class AIBrain:
    def __init__(self, model="qwen2.5:3b"):
        self.url = "http://localhost:11434/api/chat"
        self.model = model

    @property
    def available(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.ok:
                names = [item.get("name", "") for item in response.json().get("models", [])]
                return any(name == self.model or name.startswith(self.model + ":") for name in names)
        except requests.RequestException:
            pass
        return False

    def ask(self, prompt, history=None):
        messages = [{
            "role": "system",
            "content": (
                "You are a friendly desktop voice assistant running on a MacBook. "
                "Reply naturally in Hinglish (Roman Hindi mixed with simple English) "
                "when the user speaks Hinglish; otherwise match the user's language. "
                "Keep answers concise and suitable for speech."
            )
        }]
        messages.extend((history or [])[-8:])
        messages.append({"role": "user", "content": prompt})
        try:
            response = requests.post(
                self.url,
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except requests.RequestException as exc:
            print("Ollama request failed:", exc)
            return "Local AI se connect nahi ho pa raha. Check karo Ollama running hai ya nahi."
