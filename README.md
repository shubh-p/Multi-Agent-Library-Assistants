# 📚 Multi-Agent Library Assistant

An intelligent, modular library assistant application built with **LangChain**, **LangGraph**, and **Azure OpenAI**. This system uses multiple cooperating agents to simulate natural, intelligent dialogue for managing library operations like renting books, checking availability, and adding new entries.

---

## 🧠 Architecture Overview

The assistant is composed of specialized agents that coordinate to respond to user requests:

- **Coordinator Agent**  
  Routes user queries to the appropriate agent based on intent.

- **Librarian Agent**  
  Handles book-related operations like renting, returning, and listing availability.

- **Publisher Agent**  
  Responsible for scraping, adding, and updating books in the system.

All agents use Azure OpenAI’s GPT-4.1 models for intelligent language-based reasoning.

---

## 🚀 Features

- 🤖 Natural language conversation with multi-agent orchestration  
- 🔄 Book rental and return workflows  
- 🔍 Real-time availability queries  
- 🧾 Book ingestion via publisher agent (manual or scraped)  
- ☁️ Deployed using Azure OpenAI with secure key management  

---

## 🛠️ Tech Stack

- **LangChain** – For chaining agent logic  
- **LangGraph** – For orchestrating multi-agent flows  
- **Azure OpenAI (GPT-4.1)** – For agent intelligence  
- **Python** – Core language  
- **Pydantic** – Config and validation  
- **httpx & logging** – Observability and debugging  

---

## 📦 Project Structure

