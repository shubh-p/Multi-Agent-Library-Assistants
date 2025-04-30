import json
from pathlib import Path
from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langchain_core.tools.base import InjectedToolCallId
from langgraph.types import Command
from langsmith import traceable

# Path to shared library data
LIBRARY_DATA_PATH = Path("library_data.json")


def load_data():
    with open(LIBRARY_DATA_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    with open(LIBRARY_DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)


@tool
@traceable
def add_new_book(
    book_title: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """Add a new book to the library catalog."""
    data = load_data()
    books = data["books"]

    if book_title in books:
        return f"Book '{book_title}' already exists in the catalog."

    books[book_title] = {"available": True}
    save_data(data)

    return f"Book '{book_title}' has been added to the catalog."


@tool
@traceable
def scrape_old_book(
    book_title: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    """Simulate scraping metadata for an old book and add it to the catalog."""
    # For now, we simulate it with a mock addition
    data = load_data()
    books = data["books"]

    if book_title in books:
        return f"Book '{book_title}' already exists."

    books[book_title] = {"available": True}
    save_data(data)

    return f"Scraped and added old book '{book_title}' to the catalog."
