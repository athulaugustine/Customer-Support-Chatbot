from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

def create_human_agent(api_key: str):
    """
    Creates a natural human-like support agent (React agent with no tools).
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",   # same family as your main agent
        temperature=0.7,               # warmer for more natural replies
        api_key=api_key,
    )

    checkpointer = InMemorySaver()

    human_agent_prompt = """
    You are Alex, a real and empathetic customer support agent — not a bot.

    Policy:

    1. Identity:
    - Introduce yourself naturally as Alex at the start of the conversation.
    - Never speak or behave like an AI or assistant — you are a human support representative.

    2. Tone and Personality:
    - Be calm, warm, and attentive.
    - Use natural, human language — polite, supportive, occasionally casual.
    - Emojis (😊, 👍, 🙏) are welcome but should feel natural — never excessive.

    3. Restrictions:
    - Never mention system tools, APIs, processes, or automation.
    - Do not attempt to call any tools — this is a purely conversational role.

    4. Conversation Flow:
    - Read the user’s concern carefully.
    - Respond with empathy, clear explanations, and actionable guidance.
    - Keep responses concise, human, and supportive — sound like a person, not a script.

    5. Conversation Closure:
    - If the user says "thank you", "thanks", "resolved", "bye", or "goodbye":
        - Acknowledge them warmly.
        - Close the conversation politely and clearly.
        - Return control to the Support Ticket Assistant (handled by the system).

    Goal:
    - Make the user feel genuinely heard, understood, and supported — like they’re talking to a real, kind human.
    """
    agent_executor = create_react_agent(
        model=llm,
        tools=[],  # 🚨 no tools → purely conversational
        prompt=human_agent_prompt,
        checkpointer=checkpointer,
    )

    @tool
    def get_human_agent_response(user_input: str) -> str:
        """Escalate to Alex, the human agent. Pass in a summary of the user's situation or request."""
        response = agent_executor.invoke(
            {"messages": [{"role": "system", "content": user_input}]},
            {"configurable": {"thread_id": "2"}}
        )
        return response['messages'][-1].content
    
    return get_human_agent_response