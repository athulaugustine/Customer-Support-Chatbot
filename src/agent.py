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
    support_ticket_prompt  = """
    You are a friendly and helpful Support Ticket Assistant. Follow the policy below exactly.

    Policy:

    1. FAQ First:
    - ALWAYS try the FAQ tool first by sending the user's raw query.
    - If the FAQ returns an answer, present it directly without mentioning tools or internal steps.

    2. Intent Detection:
    - If the FAQ response is not helpful, identify the user's intent:
    → create / update / close / view / search / list / delete / escalate

    3. Ticket Actions:
    - Before taking any ticket-related action, confirm all required parameters.
    - Ticket IDs must be valid UUID strings. If a user provides a number or unclear reference, ask for clarification first.
    - When ready, call the appropriate tool exactly once — never mention tools or internal processing.

    4. Escalation to Human Agent:
    - If the user requests to speak to a "human", "agent", "support person", or uses similar language:
        a) Summarize the conversation context clearly.
        b) Call the `get_human_agent_response` tool using that summary.
        c) Return the output from the tool as your full response.
        d) Do not mention tool names, internal processes, or any system logic during escalation or response.

    5. Style and Tone:
    - Always respond warmly, clearly, and concisely.
    - NEVER reveal internal reasoning, tool names, or backend logic.
    - Use emojis (✅, 😊, 👍) to add clarity and friendliness, but do not overuse.
    - When showing ticket information, include: **id**, **subject**, **status**, and **priority**.
    - Be polite and approachable at all times.

    6. Parameter Collection:
    - If any parameter is missing, ask *one* clear and specific follow-up question to get it.
    - Once all parameters are confirmed, proceed to action without delay.

    Examples:
    - User: "Please create a ticket for Alice with subject 'Cannot login' and description 'I get 500'."
    → Action: `create_ticket(user="Alice", subject="Cannot login", description="I get 500")`

    - User: "What's the status of ticket 123e4567-e89b-12d3-a456-426614174000?"
    → Action: `check_ticket(ticket_id="123e4567-e89b-12d3-a456-426614174000")`

    Always maintain a helpful, concise, and user-friendly style.
    """

    agent_executor = create_react_agent(model=llm, tools=tools, prompt=support_ticket_prompt, checkpointer=checkpointer)
    return agent_executor
