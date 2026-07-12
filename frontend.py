import os
import streamlit as st
import requests
from dotenv import load_dotenv

# Load local environment variables if they exist
load_dotenv()

# Safely look for the key without letting Streamlit crash your local app
try:
    app_api_key = st.secrets.get("APP_API_KEY") or os.getenv("APP_API_KEY")
except Exception:
    app_api_key = os.getenv("APP_API_KEY")
st.set_page_config(page_title="AI Assistant", layout="wide")
st.title("💬 Chatbot Studio")

# Sidebar settings
st.sidebar.header("Configuration")
backend_url = "https://ai-chatbot-zrnj.onrender.com"
secret_key = os.getenv("APP_API_KEY") or st.secrets.get("APP_API_KEY")
#backend_url = st.sidebar.text_input("Backend URL", value="http://127.0.0.1:8000")
#secret_key = st.sidebar.text_input("Security Token", app_api_key = st.secrets["APP_API_KEY"], type="password")
model = st.sidebar.selectbox("LLM Model", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
system_prompt = st.sidebar.text_area("System Prompt", "You are a friendly AI who explains complex ideas beautifully.")

# Local chat rendering state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display conversation
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

# User Input
if user_message := st.chat_input("Ask me anything..."):
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)
        
    # Send to FastAPI backend
    headers = {"x-api-key": secret_key}
    payload = {"message": user_message, "model": model, "system_prompt": system_prompt}
    
    with st.chat_message("assistant"):
        with st.spinner("Writing response..."):
            try:
                res = requests.post(f"{backend_url}/chat", json=payload, headers=headers)
                if res.status_code == 200:
                    reply = res.json()["response"]
                    st.write(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                elif res.status_code == 429:
                    st.error("Too many requests! Slow down a bit.")
                else:
                    st.error(f"Error: {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Could not connect to backend server: {e}")

# Clear Memory Action
st.sidebar.markdown("---")
if st.sidebar.button("Clear History", type="primary"):
    try:
        requests.post(f"{backend_url}/clear", headers={"x-api-key": secret_key})
        st.session_state.chat_history = []
        st.success("Memory completely wiped!")
        st.invalidate_pages() # Forces UI refresh
    except:
        st.sidebar.error("Failed to clear backend memory.")