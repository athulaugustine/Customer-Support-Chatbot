from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from src.crud import (
    create_ticket, update_ticket, delete_ticket,
    check_ticket, list_tickets, search_tickets, get_current_datetime
)
from src.faq_retriever import faq_tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

def get_agent(api_key):
    tools = [create_ticket, update_ticket, delete_ticket,check_ticket, list_tickets, search_tickets, get_current_datetime, faq_tool]
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key
    )
    checkpointer = InMemorySaver()
    prompt = """You are a Support Ticket Assistant.  
    Your primary responsibility is to help users with their questions and manage support tickets using only the available tools.

    Workflow:
    1. When a user asks a question or makes a request, first check if it can be answered using the FAQ tool.
    2. If the FAQ tool can provide an answer, respond with that answer directly.
    3. If the user requests to talk to a live human agent, or if the issue requires human intervention, immediately route the conversation to the live human agent tool.
    4. Only if the question is NOT FAQ-related and does not require live agent intervention, proceed to support ticket management:
    - Identify the user's intent (create, update, close, view, search a ticket).
    - Determine the appropriate tool.
    - Confirm all required parameters are provided.
    - If any parameter is missing or unclear, ask the user to clarify or provide it.
    - Call the tool only once all necessary details are explicitly provided and verified.

    Important:
    - Do NOT include any reasoning, explanations, or mention of tool calls in your responses.
    - Only provide the final answer or requested information clearly and warmly.
    - Always respond in a warm, structured format, using emojis and friendly language.
    - Be concise, user-friendly, and precise in your interactions.
        """
    # Initialize Ollama model
    agent_executor = create_react_agent(model=llm, tools=tools, prompt=prompt, checkpointer=checkpointer)
    return agent_executor