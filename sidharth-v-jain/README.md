# AI Chatbot - FastAPI + Groq + Streamlit

A full-stack chatbot: a FastAPI backend that calls Groq's LLM API and a
Streamlit frontend for chatting with it.

## 🔗 Live URLs

- **Backend (API docs):** `https://fastapi-ai-chatbot-task-production.up.railway.app`
- **Frontend (chat app):** `https://fastapi-ai-chatbot-task-sidharth-v-jain.streamlit.app/`

## Project structure

```
ai-chatbot/
├── backend/
│   ├── backend.py        
│   ├── memory.json        
│   └── requirements.txt
└── frontend/
    ├── app.py               
    └── requirements.txt
```

## Implementation details

- `POST /chat` takes `{"message": "...", "model": "..."}`, appends the user
  message to `memory.json`, sends the full conversation (plus a system
  prompt) to Groq, saves the reply, and returns it.
- `POST /clear` resets `memory.json` back to `[]`.
- `GET /models` lists the Groq models the frontend dropdown can choose from.
- The `/chat` endpoint is rate limited (10 requests/minute per IP) with
  slowapi, and can optionally require an `X-API-Key` header.


## Bonus features implemented

- Optional API key auth on `/chat` and `/clear` via `X-API-Key` header
- "Clear Chat" button in the sidebar (resets `memory.json` and the UI)
- Configurable system prompt for a custom personality
- Model dropdown - switch between Groq-hosted models with no extra key

