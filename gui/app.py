"""Minimal desktop dashboard for Python Voice Assistant."""
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

import customtkinter as ctk

from assistant.voice import VoiceEngine
from assistant.ai import AIBrain
from features.calculator import calculate
from features.notes import save_note, read_notes
from features.web_tools import google_search, wikipedia_search


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python Voice Assistant")
        self.geometry("820x620")
        self.minsize(680, 520)
        self.voice = VoiceEngine()
        self.ai = AIBrain()
        self.history = []
        self.busy = False
        self._build_ui()
        self.log("Assistant ready. Type a message or press Listen.")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=14)
        header.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        ctk.CTkLabel(
            header, text="Python Voice Assistant",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=18, pady=(14, 2))
        self.status = ctk.CTkLabel(
            header, text="● Ready", text_color="#26965c"
        )
        self.status.pack(anchor="w", padx=19, pady=(0, 14))

        self.chat = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Arial", 12),
            bg="#17191d", fg="#f1f1f1", insertbackground="white",
            relief="flat", padx=14, pady=12
        )
        self.chat.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
        self.chat.configure(state="disabled")

        controls = ctk.CTkFrame(self, corner_radius=14)
        controls.grid(row=2, column=0, padx=18, pady=(8, 18), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(
            controls, placeholder_text="Type a message or command..."
        )
        self.entry.grid(row=0, column=0, padx=(12, 8), pady=12, sticky="ew")
        self.entry.bind("<Return>", lambda _event: self.send_text())
        ctk.CTkButton(controls, text="Send", width=82, command=self.send_text).grid(
            row=0, column=1, padx=5, pady=12
        )
        ctk.CTkButton(controls, text="Listen", width=82, command=self.listen_once).grid(
            row=0, column=2, padx=(5, 12), pady=12
        )
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=18, pady=(0, 12), sticky="ew")
        ctk.CTkButton(footer, text="Show Notes", width=110, command=self.show_notes).pack(side="left")
        ctk.CTkButton(footer, text="Clear Chat", width=100, fg_color="transparent",
                      border_width=1, command=self.clear_chat).pack(side="left", padx=8)
        ai_label = "AI connected" if self.ai.available else "AI key not configured"
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
        if not text or self.busy:
            return
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
            self.process_async(text)
        else:
            self.log("System: I didn't catch that. Please try again.")

    def process_async(self, text):
        self.busy = True
        self.log("You: " + text)
        self.set_status("Working...")
        threading.Thread(target=self._process_worker, args=(text,), daemon=True).start()

    def _process_worker(self, text):
        response, should_speak = self.handle_command(text)
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
            return "Goodbye. Have a nice day!", True
        if "time" in query:
            return "The time is " + datetime.now().strftime("%I:%M %p"), True
        if "date" in query:
            return "Today's date is " + datetime.now().strftime("%d %B %Y"), True
        if query in {"hello", "hi", "hey"}:
            return "Hello! Nice to meet you. How can I help?", True
        if "how are you" in query or "how r u" in query:
            return "I am fine. Thank you for asking.", True
        if "thank you" in query or query == "thanks":
            return "You're welcome. Happy to help.", True
        if query.startswith("calculate ") or query.startswith("what is "):
            expression = query.replace("calculate", "", 1).strip()
            if expression.startswith("what is "):
                expression = expression[8:]
            try:
                return "The answer is " + str(calculate(expression)), True
            except Exception:
                return "Sorry, I could not calculate that expression.", True
        if query.startswith("remember ") or query.startswith("save note "):
            note = query.split(" ", 1)[1]
            if note.startswith("note "):
                note = note[5:]
            save_note(note)
            return "Your note has been saved successfully.", True
        if "show notes" in query or "read my notes" in query:
            notes = read_notes()
            return (notes if notes else "You have no saved notes yet."), False
        if query.startswith("wikipedia "):
            term = query[len("wikipedia "):].strip()
            if term:
                wikipedia_search(term)
                return "Searching Wikipedia for " + term, True
        if query.startswith("search ") or query.startswith("search for "):
            term = query.split(" ", 1)[1].removeprefix("for ").strip()
            if term:
                google_search(term)
                return "Searching Google for " + term, True
        answer = self.ai.ask(raw, self.history)
        self.history.extend([
            {"role": "user", "content": raw},
            {"role": "assistant", "content": answer},
        ])
        return answer, True

    def show_notes(self):
        notes = read_notes()
        messagebox.showinfo("Saved Notes", notes or "No notes saved yet.")

    def clear_chat(self):
        self.chat.configure(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state="disabled")


def run():
    app = AssistantApp()
    app.mainloop()


if __name__ == "__main__":
    run()
