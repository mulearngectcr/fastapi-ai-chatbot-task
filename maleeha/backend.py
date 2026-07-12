import os
import json
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
APP_API_KEY = os.getenv("APP_API_KEY", "super_secret_handshake_token")

# Initialize Limiter (Max 10 requests per minute per user)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AI Chatbot Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

groq_client = Groq(api_key=GROQ_API_KEY)
MEMORY_FILE = "memory.json"

class ChatRequest(BaseModel):
    message: str
    model: str = "llama-3.1-8b-instant"
    system_prompt: str = "You are a helpful AI assistant."

# Security check: frontend must pass the correct password token in the header
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Security Key")
    return x_api_key

def load_history():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, data: ChatRequest, api_key: str = Depends(verify_api_key)):
    history = load_history()
    
    # Reconstruct conversation context
    messages = []
    if not history and data.system_prompt:
        messages.append({"role": "system", "content": data.system_prompt})
    messages.extend(history)
    messages.append({"role": "user", "content": data.message})
    
    try:
        completion = groq_client.chat.completions.create(
            model=data.model,
            messages=messages
        )
        bot_response = completion.choices[0].message.content
        
        # Save update to memory file
        history.append({"role": "user", "content": data.message})
        history.append({"role": "assistant", "content": bot_response})
        save_history(history)
        
        return {"response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear")
async def clear_memory(api_key: str = Depends(verify_api_key)):
    save_history([])
    return {"message": "Memory cleared"}