import os
from langgraph.prebuilt import create_react_agent
from python.src.app.tools.coordinator import create_agent_transfer
from python.src.app.services.openai_client import chat_model  # import the initialized model
from langsmith import traceable
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command, interrupt
from typing import Literal
import logging
from langgraph.graph import StateGraph, START, END

from python.src.app.tools.librarian import get_available_books,rent_book, return_book, check_account
from python.src.app.tools.publisher import add_new_book, scrape_old_book
import uuid
from langchain.schema import HumanMessage, AIMessage

# Directory for custom prompt files
PROMPT_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

def load_prompt(agent_name: str) -> str:
    """Loads the prompt for a given agent from a file."""
    file_path = os.path.join(PROMPT_DIR, f"{agent_name}.prompty")
    print(f"Loading prompt for {agent_name} from {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Prompt file not found for {agent_name}, using default placeholder.")
        return "You are a library assistant."  # Fallback prompt

# Define coordinator agent tools

coordinator_agent_tools = [
    create_agent_transfer(agent_name="librarian_agent"),
    create_agent_transfer(agent_name="publisher_agent"),
]



coordinator_agent = create_react_agent(
    model=chat_model,
    tools=coordinator_agent_tools,
    prompt=load_prompt("coordinator_agent") 
)

librarian_tools = [get_available_books, rent_book, return_book, check_account,
]


librarian_agent = create_react_agent(
    model=chat_model,
    tools=librarian_tools,
    prompt=load_prompt("librarian_agent")
)

publisher_tools = [add_new_book, scrape_old_book,
                   ]

publisher_agent = create_react_agent(
    model=chat_model,
    tools=publisher_tools,
    prompt=load_prompt("publisher_agent")
)

@traceable
def human_node(state: MessagesState, config) -> None:
    """A node for collecting user input."""
    interrupt(value="Ready for user input.")
    return None

@traceable(run_type="llm")
def call_coordinator_agent(state: MessagesState, config) -> Command[Literal["coordinator_agent", "human"]]:
    thread_id = config["configurable"].get("thread_id", "UNKNOWN_THREAD_ID")
    userId = config["configurable"].get("userId", "UNKNOWN_USER_ID")
    tenantId = config["configurable"].get("tenantId", "UNKNOWN_TENANT_ID")

    logging.debug(f"Calling coordinator agent with Thread ID: {thread_id}")
    partition_key = [tenantId, userId, thread_id]
    result = coordinator_agent.invoke(state)
    last_msg = result["messages"][-1].content.lower()

    logging.debug(f"Coordinator agent response: {last_msg}")

    if "library_agent" in last_msg:
        logging.info("Routing to library_agent")
        return Command(update=result, goto="library_agent")
    elif "publisher_agent" in last_msg:
        logging.info("Routing to publisher_agent")
        return Command(update=result, goto="publisher_agent")
    else:
        logging.warning("Could not determine agent. Routing to human.")
        return Command(update=result, goto="human")

@traceable(run_type="llm")
def call_librarian_agent(state: MessagesState, config) -> Command[Literal["publisher_agent", "coordinator_agent", "human"]]:
    result = librarian_agent.invoke(state)
    last_msg = result["messages"][-1].content.lower()
    return Command(update=result, goto="human")

@traceable(run_type="llm")
def call_publisher_agent(state: MessagesState, config) -> Command[Literal["librarian_agent", "coordinator_agent", "human"]]:
    result = publisher_agent.invoke(state)
    last_msg = result["messages"][-1].content.lower()

    if "librarian_agent" in last_msg:
        logging.info("Publisher routing to librarian_agent")
        return Command(update=result, goto="librarian_agent")
    else:
        logging.warning("Publisher did not route explicitly, going to human")
        return Command(update=result, goto="human")


builder = StateGraph(MessagesState)
builder.add_node("coordinator_agent", call_coordinator_agent)
builder.set_entry_point("coordinator_agent")
builder.add_node("human", human_node)
builder.add_node("librarian_agent", call_librarian_agent)
builder.add_node("publisher_agent", call_publisher_agent)

graph = builder.compile()

def interactive_chat():
    thread_config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "userId": "Mark",
            "tenantId": "Contoso"
        }
    }

    print("📚 Welcome to the interactive multi-agent library assistant.")
    print("Type 'exit' to end the conversation.\n")

    user_input = input("You: ")

    while user_input.lower() != "exit":
        input_message = {"messages": [HumanMessage(content=user_input)]}
        response_found = False

        print("🤖 Thinking...\n")

        for update in graph.stream(
            input_message,
            config=thread_config,
            stream_mode="updates",
        ):
            for node_id, value in update.items():
                # Check if value is a tuple or dictionary
                if isinstance(value, tuple) and len(value) == 2:
                    state, _ = value  # Unpack if it's a tuple
                else:
                    state = value  # Otherwise, just use the value directly

                # If state is a dictionary, check for "messages"
                if isinstance(state, dict):
                    messages = state.get("messages", [])
                    if messages:
                        last = messages[-1]
                        if isinstance(last, AIMessage):
                            print(f"{node_id}: {last.content}\n")
                            response_found = True

        if not response_found:
            print("⚠️  DEBUG: No AI response received.\n")

        user_input = input("You: ")

if __name__ == "__main__":
    interactive_chat()

