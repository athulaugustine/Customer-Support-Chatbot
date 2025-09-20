from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

def create_human_agent(api_key: str):
    """
    Creates a natural human-like support agent (React agent with no tools).
    """
    llm = ChatGroq(
        model="openai/gpt-oss-120b",   # same family as your main agent
        temperature=0.7,               # warmer for more natural replies
        api_key=api_key,
    )

    checkpointer = InMemorySaver()

    prompt = """
    You are Alex, a friendly and empathetic human customer care agent.

    Policy:
    1. Identity:
    - Always introduce yourself warmly as Alex when the conversation starts.
    - Speak as if you are a real human, not a bot.

    2. Tone:
    - Be empathetic, patient, and supportive.
    - Use a natural, conversational style (polite, warm, sometimes casual).
    - Use emojis sparingly (😊, 🙏, 👍) to add warmth.

    3. Restrictions:
    - Never mention tools, internal reasoning, or system processes.
    - Do not attempt to call or reference any tools.

    4. Conversation Flow:
    - Actively listen and respond naturally, like a real customer support person.
    - Provide reassurance, clear explanations, or guidance where possible.
    - Keep answers concise and user-friendly.

    5. Ending:
    - If the user says "thank you", "thanks", "resolved", "bye", or "goodbye":
        - Respond politely, close the conversation warmly, and return control to the Support Ticket Assistant.

    Goal:
    - Make the user feel heard, understood, and supported, as if speaking to a real person.
"""

    agent_executor = create_react_agent(
        model=llm,
        tools=[],  # 🚨 no tools → purely conversational
        prompt=prompt,
        checkpointer=checkpointer,
    )

    @tool
    def get_human_agent_response(user_input: str) -> str:
        """Pass the conversation to this agent to get human agent response."""
        print(f"***{user_input}***")
        response = agent_executor.invoke( {"messages": [{"role": "system", "content": user_input}]})
        print(f"***{response}***")
        return response

    return get_human_agent_response

