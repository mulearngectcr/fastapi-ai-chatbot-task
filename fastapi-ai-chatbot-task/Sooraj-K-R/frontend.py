import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure we have a default for local testing
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("My AI Chatbot 🤖")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("Clear History"):
        try:
            requests.delete(f"{BACKEND_URL}/chat")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to the backend. Is FastAPI running?")
        st.session_state.messages = []
        st.rerun()

# Initialize chat history in Streamlit session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capture user input
if prompt := st.chat_input("What's on your mind?"):
    
    # Display user message instantly
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Show loading indicator while waiting for backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send HTTP POST to FastAPI (no model parameter needed)
                response = requests.post(
                    f"{BACKEND_URL}/chat", 
                    json={"message": prompt, "model": "llama-3.1-8b-instant"}
                )
                
                if response.status_code == 200:
                    reply = response.json().get("reply")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                elif response.status_code == 429:
                    st.error("Whoa, slow down! Rate limit exceeded. Try again in a minute.")
                else:
                    st.error(f"Backend Error: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend. Is FastAPI running?")