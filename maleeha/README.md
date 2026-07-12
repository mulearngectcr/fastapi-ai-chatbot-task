# 🤖 AI Chatbot Studio (FastAPI + Streamlit + Groq)

A secure, production-ready, full-stack AI chatbot application featuring a high-performance **FastAPI** backend endpoint and an intuitive **Streamlit** user interface. The project leverages Groq Cloud infrastructure for incredibly fast, low-latency LLM inference.

---

## 🚀 Live Production Links
*   **Frontend UI (Streamlit Cloud):** `https://aichatbot-ae4heesrkjscwqorrkucld.streamlit.app/`
*   **Backend API Documentation (Render /docs):** `https://ai-chatbot-zrnj.onrender.com/docs`

---

## ✨ Core Features Built

### 🧱 Backend Architecture (`backend.py`)
*   **FastAPI Endpoint:** Secure POST `/chat` endpoint utilizing Pydantic models for structured data validation.
*   **Rate Limiting:** Guarded by `slowapi` (configured for a maximum of 10 requests/min per IP) to prevent endpoint abuse and manage api limits.
*   **Custom API Authentication (Bonus):** Implemented header-based security checks (`x-api-key`) to restrict unauthorized API execution.
*   **Persistent Chat Context:** Conversational history managed reliably through automated reading/writing to a local `memory.json` array.
*   **Memory Reset (Bonus):** Added a `/clear` endpoint to wipe the chat history programmatically.

### 🎨 Frontend UI (`frontend.py`)
*   **Streamlit Chat Interface:** Built an immersive chat window leveraging native `st.chat_input` and `st.chat_message` components.
*   **Loading States:** Features a live `st.spinner` ("Writing response...") while waiting for the async backend completion.
*   **Dynamic Configurations (Bonus):**
    *   **Model Selector Dropdown:** Allows users to switch on the fly between upgraded Groq production models (`llama-3.1-8b-instant`).
    *   **System Prompt Editor:** Allows editing of the chatbot's custom persona/instructions dynamically.
    *   **Clear Chat Button:** One-click history wiper that clears both local session state and the backend JSON file.

---

## 📋 Tech Stack Used
*   **Backend framework:** FastAPI, Uvicorn, Slowapi, Pydantic
*   **LLM Engine:** Groq Cloud SDK
*   **Frontend framework:** Streamlit, Requests
*   **Environment Management:** Python-dotenv

---

## 📦 How to Setup and Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/ai-chatbot.git](https://github.com/YOUR_GITHUB_USERNAME/ai-chatbot.git)
   cd ai-chatbot