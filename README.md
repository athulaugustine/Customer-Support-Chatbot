# Customer Support Chatbot
A Streamlit-based AI-powered customer support assistant that answers FAQs, manages support tickets, and routes queries to human agents when needed.
<img width="1906" height="985" alt="image" src="https://github.com/user-attachments/assets/23102c4e-88cd-4f84-a77e-031831f0f225" />
<img width="1909" height="989" alt="image" src="https://github.com/user-attachments/assets/34cad26f-1c4c-442d-8c90-6d468e425b2c" />

# 🖥️ App Preview
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://customer-support-chatbot-zoaqv9nmdgfrje8joiecow.streamlit.app/)

## Features

- **FAQ Retrieval:** Uses semantic search and vector database (FAISS) to answer common questions from an Excel FAQ file.
- **Support Ticket Management:** Create, update, search, and manage support tickets using a SQLite database and SQLAlchemy ORM.
- **AI Agent:** Integrates with Groq LLM (Llama 3) for natural language understanding and decision-making.
- **Human Escalation:** Routes queries to human agents when required.
- **Streamlit UI:** Interactive chat interface for users.

## Project Structure

```
requirements.txt
streamlit_app.py
faqs/
    customer_support_chatbot_faqs.xlsx
src/
    agent.py
    crud.py
    db.py
    faq_retriever.py
    human_agent.py
    models.py
    __pycache__/
data/
    tickets.db
```

## Setup

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Prepare FAQ data:**
   - Place your FAQ Excel file in `faqs/customer_support_chatbot_faqs.xlsx`.

3. **Run the app:**
   ```powershell
   streamlit run streamlit_app.py
   ```

4. **Set your Groq API key** in the app UI to enable LLM features.

## Key Files

- `streamlit_app.py`: Main Streamlit UI and chat logic.
- `src/agent.py`: Assembles the AI agent and tool routing.
- `src/faq_retriever.py`: Loads FAQ data, builds vector index, and retrieves answers.
- `src/crud.py`: Ticket management tools (create, update, search, etc.).
- `src/models.py`: SQLAlchemy models for tickets and enums.
- `src/db.py`: Database setup and session management.
- `faqs/customer_support_chatbot_faqs.xlsx`: FAQ data source.

## Requirements

See `requirements.txt` for all Python dependencies.

## How It Works

- User interacts via chat in Streamlit.
- Agent first tries to answer using FAQ retrieval.
- If FAQ is insufficient, agent detects intent and manages tickets or escalates to a human agent.
- All ticket data is stored in a local SQLite database.

## License

MIT License (add your own if needed).
