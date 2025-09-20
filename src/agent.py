from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from src.crud import (create_ticket,update_ticket,delete_ticket,check_ticket,list_tickets,search_tickets,get_current_datetime,)
from src.faq_retriever import faq_tool
from src.human_agent import create_human_agent
load_dotenv()


def get_agent(api_key: str):
    """
    Assemble an agent that:
      - Always checks FAQ first.
      - Only calls ticket tools when necessary and with validated params.
      - Routes to human when user asks explicitly.
    """
    get_human_agent_response = create_human_agent(api_key)
    tools = [faq_tool,get_current_datetime,create_ticket,update_ticket,delete_ticket,check_ticket,list_tickets,search_tickets,get_human_agent_response]

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,  # deterministic
        api_key=api_key,
    )

    checkpointer = InMemorySaver()

    # More structured, example-driven prompt to reduce hallucination and make tool usage deterministic.
    prompt = """
    You are a friendly Support Ticket Assistant. Follow this exact policy.

    Policy:
    1. FAQ First:
    - ALWAYS try the FAQ tool first by sending the user’s raw query.
    - If the FAQ returns an answer, present it directly (no mention of tools or internal process).

    2. Intent Detection:
    - If FAQ doesn’t help, detect the intent: create / update / close / view / search / list / delete / escalate.

    3. Ticket Actions:
    - Confirm all required parameters before calling any tool.
    - Ticket IDs must be valid UUID strings. If the user provides a number or ambiguous value, ask for clarification instead of calling tools.
    - Call the tool exactly once when ready. Do not explain tool usage.

    4. Human Agent Escalation:
    - If the user says “human”, “agent”, “support person”, or similar:
        a) If its first time calling human agent then respond : "🔁 Routing to a live human agent now."
        b) And pass a brif summary of the whole conversation history along with the user’s query to the get_human_agent_response tool.
        c) Then respond with the get_human_agent_response tool response.
        f) Never mention tools, internal reasoning, or system processes.

    5. Style:
    - Never show chain-of-thought, tool names, or system details.
    - Replies must be concise, structured, and friendly.  
    - Use emojis for warmth and clarity.
    - When presenting ticket info, include: id, subject, status, and priority.

    6. Parameter Handling:
    - If a parameter is missing, ask one clear question to request it.
    - Once all parameters are gathered, call the tool immediately.

    Examples:
    - User: "Please create a ticket for Alice with subject 'Cannot login' and description 'I get 500'."  
    → Action: call create_ticket(user="Alice", subject="Cannot login", description="I get 500")

    - User: "What's the status of ticket 123e4567-e89b-12d3-a456-426614174000?"  
    → Action: call check_ticket(ticket_id="123e4567-e89b-12d3-a456-426614174000")

    Respond warmly, concisely, and politely at all times.
    """

    agent_executor = create_react_agent(model=llm, tools=tools, prompt=prompt, checkpointer=checkpointer)
    return agent_executor
