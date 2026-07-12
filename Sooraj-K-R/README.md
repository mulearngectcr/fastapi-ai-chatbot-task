# AI Chatbot — FastAPI + Streamlit + Groq

A conversational AI chatbot built with a **FastAPI** backend and a **Streamlit** frontend, powered by **Groq's LLaMA 3.1** model. The app supports persistent conversation memory, rate limiting, and a clean chat UI.

---

## Features

| Feature | Details |
|---|---|
| **LLM Backend** | Groq API with `llama-3.1-8b-instant` model |
| **Conversation Memory** | Chat history persisted to `memory.json` |
| **Rate Limiting** | 5 requests/minute per client (via SlowAPI) |
| **Chat UI** | Streamlit-based interface with message history |
| **Clear History** | One-click button to reset the conversation |

---

## Project Structure

```
Sooraj-K-R/
├── backend.py         # FastAPI server with /chat endpoints
├── frontend.py        # Streamlit chat interface
├── requirements.txt   # Python dependencies
├── .env               # API keys (not tracked by git)
└── .gitignore
```

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://127.0.0.1:8000
```

Get your Groq API key from [console.groq.com](https://console.groq.com/).

### 3. Run the Backend

```bash
uvicorn backend:app --reload
```

### 4. Run the Frontend (in a separate terminal)

```bash
streamlit run frontend.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Send a message and receive an AI reply |
| `DELETE` | `/chat` | Clear the conversation history |

### POST `/chat` — Request Body

```json
{
  "message": "Hello, how are you?",
  "model": "llama-3.1-8b-instant"
}
```

### POST `/chat` — Response

```json
{
  "reply": "I'm doing great! How can I help you today?"
}
```

---

## Tech Stack

- **FastAPI** — async API framework
- **Streamlit** — frontend chat UI
- **Groq** — LLM inference (LLaMA 3.1)
- **SlowAPI** — rate limiting middleware
- **Pydantic** — request validation

---

## Author

**Sooraj K R**
