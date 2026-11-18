"""Entry point for the upgraded Python Voice Assistant.

The original command-line implementation is preserved on the main branch.
This branch launches the new modular desktop application.
"""
from dotenv import load_dotenv

load_dotenv()

from gui.app import run


if __name__ == "__main__":
    run()
