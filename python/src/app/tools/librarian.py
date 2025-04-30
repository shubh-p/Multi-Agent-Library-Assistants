import json
from langchain_core.tools import tool
from typing import Annotated
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langsmith import traceable

LIBRARY_DATA_PATH = "library_data.json"


def load_library_data():
    with open(LIBRARY_DATA_PATH, "r") as f:
        return json.load(f)


def save_library_data(data):
    with open(LIBRARY_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


@tool
@traceable
def get_available_books() -> str:
    """Returns a list of books currently available in the library."""
    data = load_library_data()
    available = [title for title, info in data["books"].items() if info["available"]]
    return f"Available books: {', '.join(available)}" if available else "No books available."


@tool
@traceable
def rent_book(book_title: str, user_id: str) -> str:
    """Rent a book for a user, if available."""
    data = load_library_data()
    if book_title not in data["books"]:
        return f"Book '{book_title}' not found."

    if not data["books"][book_title]["available"]:
        return f"Book '{book_title}' is currently rented."

    data["books"][book_title]["available"] = False
    data["accounts"].setdefault(user_id, {"rented_books": [], "history": [], "fines_due": 0.0})
    data["accounts"][user_id]["rented_books"].append(book_title)
    data["accounts"][user_id]["history"].append(book_title)

    save_library_data(data)
    return f"Book '{book_title}' has been rented to user '{user_id}'."

@tool
@traceable
def return_book(book_title: str, user_id: str) -> str:
    """Return a rented book."""
    data = load_library_data()
    if book_title not in data["accounts"].get(user_id, {}).get("rented_books", []):
        return f"User '{user_id}' did not rent '{book_title}'."

    data["books"][book_title]["available"] = True
    data["accounts"][user_id]["rented_books"].remove(book_title)

    save_library_data(data)
    return f"Book '{book_title}' returned successfully by user '{user_id}'."


@tool
@traceable
def check_account(user_id: str) -> str:
    """Check the user's rented books, history, and outstanding fines."""
    data = load_library_data()
    account = data["accounts"].get(user_id)

    if not account:
        return f"No account found for user '{user_id}'."

    rented = ", ".join(account["rented_books"]) or "None"
    history = ", ".join(account["history"]) or "None"
    fines = account["fines_due"]

    return f"Account '{user_id}':\n- Rented: {rented}\n- History: {history}\n- Fines Due: ${fines}"
