import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.agent import get_agent
import uuid
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Prevent duplicate handlers during reloads (common in Streamlit)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

st.title("💬 Customer Support Chatbot")
groq_api_key = st.text_input("Groq API Key", type="password")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_config" not in st.session_state:
        st.session_state.agent_config = {"configurable": {"thread_id": uuid.uuid4()}}
    if "agent" not in st.session_state:
        st.session_state.agent = get_agent(groq_api_key)

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] != "system":  # Skip system message in chat display
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What can I help you with?"):
        # Append user input to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user input
        with st.chat_message("user"):
            st.markdown(prompt)

        # Collect messages for LLM input
        chat_history = [
            HumanMessage(content=m["content"]) if m["role"] == "user"
            else AIMessage(content=m["content"]) if m["role"] == "assistant"
            else SystemMessage(content=m["content"])
            for m in st.session_state.messages
        ]

        # Stream and display assistant's response
        with st.chat_message("assistant"):
            response_text = ""
            response_area = st.empty()
            for chunk in st.session_state.agent.stream({"messages": [{"role": "user", "content": prompt}]},stream_mode="updates", config= st.session_state.agent_config["configurable"]):
                logger.info(chunk)
                if 'agent' in chunk:
                    response_text += chunk['agent']['messages'][-1].content
                elif 'tools' in chunk:
                    st.toast(chunk['tools']['messages'][-1].content)
                response_area.markdown(response_text)

        # Append assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
