# AI Chatbot — FastAPI + Groq + Streamlit

A full-stack chatbot: a FastAPI backend that calls Groq's LLM API and a
Streamlit frontend for chatting with it.

## 🔗 Live URLs

- **Backend (API docs):** `<paste your Render/Railway URL>/docs`
- **Frontend (chat app):** `<paste your Streamlit Cloud URL>`

## Project structure

```
ai-chatbot/
├── backend/
│   ├── backend.py            # FastAPI app
│   ├── memory.json           # conversation history (starts as [])
│   ├── requirements.txt
│   ├── .env.example
│   └── render.yaml           # optional one-click Render config
└── frontend/
    ├── app.py                # Streamlit chat UI
    ├── requirements.txt
    └── .streamlit/secrets.toml.example
```

## How it works

- `POST /chat` takes `{"message": "...", "model": "..."}`, appends the user
  message to `memory.json`, sends the full conversation (plus a system
  prompt) to Groq, saves the reply, and returns it.
- `POST /clear` resets `memory.json` back to `[]`.
- `GET /models` lists the Groq models the frontend dropdown can choose from.
- The `/chat` endpoint is rate-limited (10 requests/minute per IP) with
  `slowapi`, and can optionally require an `X-API-Key` header.

## Run it locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste in your real GROQ_API_KEY
uvicorn backend:app --reload
```

The API is now at `http://localhost:8000` — check `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # set BACKEND_URL
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Deployment

### Backend → Render (or Railway)

**Render:**
1. Push this repo to GitHub.
2. On [render.com](https://render.com) → New → Web Service → connect the repo,
   set root directory to `backend`.
3. Build command: `pip install -r requirements.txt`
   Start command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`
4. Add environment variables: `GROQ_API_KEY` (required), `BACKEND_API_KEY`
   and `SYSTEM_PROMPT` (optional).
5. Deploy, then verify at `https://<your-service>.onrender.com/docs`.

**Railway:** same idea — New Project → Deploy from GitHub → set root
directory to `backend`, add the same env vars, Railway auto-detects the
start command from `requirements.txt`/`Procfile` conventions (or set it
manually to the uvicorn command above).

### Frontend → Streamlit Cloud

1. On [share.streamlit.io](https://share.streamlit.io), New app → pick this
   repo → set main file path to `frontend/app.py`.
2. In **Settings → Secrets**, add:
   ```toml
   BACKEND_URL = "https://<your-deployed-backend>.onrender.com"
   BACKEND_API_KEY = ""
   ```
3. Deploy. The app will call your live backend, not localhost.

(Option 2 frontends — plain HTML/JS or React — deploy the same way to
Vercel/Netlify/GitHub Pages, calling the same backend URL via `fetch`/`axios`.)

## Environment variables (backend/.env)

| Variable          | Required | Purpose                                             |
|--------------------|----------|------------------------------------------------------|
| `GROQ_API_KEY`     | Yes      | Your Groq API key ([console.groq.com/keys](https://console.groq.com/keys)) |
| `BACKEND_API_KEY`  | No       | If set, `/chat` and `/clear` require header `X-API-Key: <value>` |
| `SYSTEM_PROMPT`    | No       | Overrides the bot's default personality              |

## Bonus features implemented

- ✅ Optional API key auth on `/chat` and `/clear` via `X-API-Key` header
- ✅ "Clear Chat" button in the sidebar (resets `memory.json` and the UI)
- ✅ Configurable system prompt for a custom personality
- ✅ Model dropdown — switch between Groq-hosted models with no extra key

## Testing checklist before submitting

- [ ] Hit `<backend-url>/docs`, try `/chat` there directly
- [ ] Open the deployed Streamlit app, send a message, confirm a reply appears
- [ ] Refresh the Streamlit app — history should persist via `memory.json` on reload of backend-fed state
- [ ] Click "Clear Chat" and confirm history empties
- [ ] Confirm frontend is pointed at the deployed backend URL, not `localhost`
