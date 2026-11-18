"""Persistent notes stored locally in the project folder."""
from pathlib import Path

NOTES_FILE = Path(__file__).resolve().parent.parent / "notes.txt"


def save_note(note: str) -> None:
    with NOTES_FILE.open("a", encoding="utf-8") as file:
        file.write(note.strip() + "\n")


def read_notes() -> str:
    if not NOTES_FILE.exists():
        return ""
    return NOTES_FILE.read_text(encoding="utf-8").strip()
