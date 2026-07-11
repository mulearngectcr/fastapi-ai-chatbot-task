import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_KEY = st.secrets.get("BACKEND_API_KEY", "")  

st.set_page_config(page_title="AI Chatbot", page_icon="💬")
st.title("💬 AI Chatbot")


def api_headers() -> dict:
    return {"X-API-Key": API_KEY} if API_KEY else {}


@st.cache_data(ttl=300)
def fetch_models() -> tuple[list[str], str]:
    try:
        resp = requests.get(f"{BACKEND_URL}/models", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["models"], data["default"]
    except requests.RequestException:
        return ["llama-3.3-70b-versatile"], "llama-3.3-70b-versatile"


with st.sidebar:
    st.header("Settings")

    models, default_model = fetch_models()
    selected_model = st.selectbox("Groq model", models, index=models.index(default_model))

    if st.button("🗑️ Clear Chat", use_container_width=True):
        try:
            requests.post(f"{BACKEND_URL}/clear", headers=api_headers(), timeout=10)
        except requests.RequestException as exc:
            st.error(f"Could not clear chat on the server: {exc}")
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": user_input, "model": selected_model},
                    headers=api_headers(),
                    timeout=60,
                )
                resp.raise_for_status()
                reply = resp.json()["reply"]
            except requests.RequestException as exc:
                reply = f"⚠️ Error talking to backend: {exc}"
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
