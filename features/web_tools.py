"""Browser helpers."""
import webbrowser
from urllib.parse import quote_plus


def google_search(query: str) -> None:
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))


def wikipedia_search(query: str) -> None:
    webbrowser.open("https://en.wikipedia.org/w/index.php?search=" + quote_plus(query))
