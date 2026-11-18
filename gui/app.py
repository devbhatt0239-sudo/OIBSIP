"""Desktop dashboard for the Python Voice Assistant."""
import subprocess
import threading
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from datetime import datetime

import customtkinter as ctk

from assistant.voice import VoiceEngine
from assistant.ai import AIBrain
from features.calculator import calculate
from features.notes import save_note, read_notes
from features.web_tools import google_search, wikipedia_search
from features.mac_tools import open_mac_app, set_volume, get_weather

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python Voice Assistant")
        self.geometry("900x680")
        self.minsize(720, 560)
        self.voice = VoiceEngine()
        self.ai = AIBrain()
        self.memory_file = Path(__file__).resolve().parent.parent / "assistant_memory.json"
        self.history = self._load_memory()
        self.busy = False
        self._build_ui()
        self.log("Assistant ready! Type a command or press Listen.")
        
    def _load_memory(self):
        try:
            if self.memory_file.exists():
                data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def _save_memory(self):
        try:
            self.memory_file.write_text(
                json.dumps(self.history[-40:], ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except OSError as exc:
            print("Could not save assistant memory:", exc)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self, corner_radius=14)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        ctk.CTkLabel(header, text="Python Voice Assistant",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=18, pady=(14, 2))
        self.status = ctk.CTkLabel(header, text="● Ready", text_color="#26965c")
        self.status.pack(anchor="w", padx=19, pady=(0, 14))
        self.chat = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Arial", 12),
            bg="#17191d", fg="#f1f1f1", insertbackground="white",
            relief="flat", padx=14, pady=12)
        self.chat.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
        self.chat.configure(state="disabled")
        controls = ctk.CTkFrame(self, corner_radius=14)
        controls.grid(row=2, column=0, padx=18, pady=(8, 8), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(controls, placeholder_text="Try: calculate 12*5, open Safari, weather Jaipur...")
        self.entry.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="ew")
        self.entry.bind("<Return>", lambda _event: self.send_text())
        ctk.CTkButton(controls, text="Send", width=82, command=self.send_text).grid(row=0, column=1, padx=5, pady=12)
        ctk.CTkButton(controls, text="Listen", width=82, command=self.listen_once).grid(row=0, column=2, padx=(5, 12), pady=12)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=18, pady=(0, 14), sticky="ew")
        ctk.CTkButton(footer, text="Calculator", width=100, command=self.calculator_dialog).pack(side="left", padx=(0, 7))
        ctk.CTkButton(footer, text="Show Notes", width=105, command=self.show_notes).pack(side="left", padx=7)
        ctk.CTkButton(footer, text="Open Safari", width=105, command=lambda: self.process_async("open Safari")).pack(side="left", padx=7)
        ctk.CTkButton(footer, text="Clear Chat", width=95, fg_color="transparent",
                      border_width=1, command=self.clear_chat).pack(side="left", padx=7)
        ai_label = "Local AI connected" if self.ai.available else "Start Ollama to connect AI"
        ctk.CTkLabel(footer, text=ai_label).pack(side="right", padx=8)

    def log(self, text):
        self.chat.configure(state="normal")
        self.chat.insert(tk.END, text + "\n\n")
        self.chat.see(tk.END)
        self.chat.configure(state="disabled")

    def set_status(self, text):
        self.status.configure(text="● " + text)

    def send_text(self):
        text = self.entry.get().strip()
        if text and not self.busy:
            self.entry.delete(0, tk.END)
            self.process_async(text)

    def listen_once(self):
        if self.busy:
            return
        self.busy = True
        self.set_status("Listening...")
        self.log("Assistant: Listening...")
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        text = self.voice.listen()
        self.after(0, lambda: self._finish_listen(text))

    def _finish_listen(self, text):
        self.busy = False
        self.set_status("Ready")
        if text.startswith("__ERROR__:"):
            self.log("System: " + text.replace("__ERROR__:", ""))
        elif text:
            cleaned = text.strip()
            if cleaned.lower().startswith("hey assistant"):
                cleaned = cleaned[len("hey assistant"):].strip(" ,")
            if cleaned:
                self.process_async(cleaned)
            else:
                self.log("Assistant: Yes, I'm listening. What can I do?")
        else:
            self.log("System: I didn't catch that. Please try again.")

    def process_async(self, text):
        self.busy = True
        self.log("You: " + text)
        self.set_status("Working...")
        threading.Thread(target=self._process_worker, args=(text,), daemon=True).start()

    def _process_worker(self, text):
        try:
            response, should_speak = self.handle_command(text)
        except Exception as exc:
            response, should_speak = f"Something went wrong: {exc}", False
        self.after(0, lambda: self._show_response(response))
        if should_speak and response:
            try:
                self.voice.speak(response)
            except Exception as exc:
                print("Speech output error:", exc)
        self.after(0, self._ready)

    def _show_response(self, response):
        if response:
            self.log("Assistant: " + response)

    def _ready(self):
        self.busy = False
        self.set_status("Ready")

    def handle_command(self, raw):
        query = raw.lower().strip()
        if query in {"exit", "quit", "close assistant"}:
            self.after(300, self.destroy)
            return "Goodbye!", True
        if query in {"hello", "hi", "hey", "hey assistant"}:
            return "Hello! Main ready hoon. Batao kya karna hai?", True
        if "time" in query:
            return "The time is " + datetime.now().strftime("%I:%M %p"), True
        if "date" in query:
            return "Today's date is " + datetime.now().strftime("%d %B %Y"), True
        if "how are you" in query or "how r u" in query:
            return "Main bilkul theek hoon! How can I help?", True
        if query.startswith(("calculate ", "what is ")):
            expression = query[9:].strip() if query.startswith("calculate ") else query[8:].strip()
            try:
                return "The answer is " + str(calculate(expression)), True
            except Exception:
                return "Sorry, I could not calculate that expression.", True
        if query.startswith(("remember ", "save note ")):
            note = raw.split(" ", 1)[1]
            if note.lower().startswith("note "):
                note = note[5:]
            save_note(note)
            return "Your note has been saved.", True
        if "show notes" in query or "read my notes" in query:
            return read_notes() or "You have no saved notes yet.", False
        if query.startswith("open "):
            app_name = raw[5:].strip()
            try:
                open_mac_app(app_name)
                return "Opening " + app_name, True
            except Exception:
                return "I couldn't open " + app_name + ". Check the app name.", True
        if "volume" in query:
            if "mute" in query:
                set_volume(0)
                return "Volume muted.", True
            digits = "".join(ch for ch in query if ch.isdigit())
            level = int(digits) if digits else (70 if "up" in query or "increase" in query else 35)
            level = max(0, min(100, level))
            set_volume(level)
            return f"Volume set to {level} percent.", True
        if "weather" in query:
            place = raw.lower().replace("weather", "").replace("in ", "").strip() or "Jaipur"
            return get_weather(place), True
        if query.startswith("wikipedia "):
            term = raw[10:].strip()
            wikipedia_search(term)
            return "Searching Wikipedia for " + term, True
        if query.startswith(("search ", "search for ")):
            term = raw.split(" ", 1)[1].removeprefix("for ").strip()
            google_search(term)
            return "Searching Google for " + term, True
        answer = self.ai.ask(raw, self.history)
        self.history.extend([{"role": "user", "content": raw},
                             {"role": "assistant", "content": answer}])
        self._save_memory()
        return answer, True

    def calculator_dialog(self):
        expression = simpledialog.askstring("Calculator", "Enter a calculation (e.g. 25 + 15):", parent=self)
        if expression:
            try:
                result = calculate(expression)
                self.log(f"You: calculate {expression}\nAssistant: The answer is {result}")
                self.voice.speak(f"The answer is {result}")
            except Exception:
                messagebox.showerror("Calculator", "Invalid calculation.")

    def show_notes(self):
        messagebox.showinfo("Saved Notes", read_notes() or "No notes saved yet.")

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state="disabled")


def run():
    AssistantApp().mainloop()


if __name__ == "__main__":
    run()
