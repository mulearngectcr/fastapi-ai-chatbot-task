import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from groq import Groq
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a friendly, concise assistant with a warm sense of humor.",
)

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is missing. Add it to your .env file.")

client = Groq(api_key=GROQ_API_KEY)
MEMORY_FILE = Path(__file__).parent / "memory.json"

AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]
DEFAULT_MODEL = AVAILABLE_MODELS[0]

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="AI Chatbot API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(api_key_header)) -> None:
    """If BACKEND_API_KEY is set in .env, require a matching X-API-Key header."""
    if BACKEND_API_KEY and key != BACKEND_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def load_history() -> list[dict]:
    if not MEMORY_FILE.exists():
        return []
    try:
        return json.loads(MEMORY_FILE.read_text())
    except json.JSONDecodeError:
        return []


def save_history(history: list[dict]) -> None:
    MEMORY_FILE.write_text(json.dumps(history, indent=2))


class ChatRequest(BaseModel):
    message: str
    model: str = DEFAULT_MODEL


class ChatResponse(BaseModel):
    reply: str
    history: list[dict]


@app.get("/")
def root():
    return {"status": "ok", "message": "Chatbot API is running. See /docs."}


@app.get("/models")
def get_models():
    return {"models": AVAILABLE_MODELS, "default": DEFAULT_MODEL}


@app.post("/chat", response_model=ChatResponse, dependencies=[Security(verify_api_key)])
@limiter.limit("10/minute")
def chat(request: Request, payload: ChatRequest):
    history = load_history()
    history.append({"role": "user", "content": payload.message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    try:
        completion = client.chat.completions.create(
            model=payload.model,
            messages=messages,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq API error: {exc}") from exc

    reply = completion.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    save_history(history)

    return ChatResponse(reply=reply, history=history)


@app.post("/clear", dependencies=[Security(verify_api_key)])
def clear_history():
    save_history([])
    return {"status": "cleared"}
