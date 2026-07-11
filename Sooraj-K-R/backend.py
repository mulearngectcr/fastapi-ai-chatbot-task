import os
import json
from fastapi import FastAPI,Request,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import AsyncGroq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

client = AsyncGroq(api_key = os.getenv("GROQ_API_KEY"))
MEMORY_FILE = "memory.json"

class ChatRequest(BaseModel):
    message:str
    model: str = "llama-3.1-8b-instant"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE,"r") as f:
        return json.load(f)

def save_memory(history):
    with open(MEMORY_FILE,"w") as f:
        json.dump(history,f, indent=4)
    
@app.post("/chat")
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    history = load_memory()

    if not history:
        history.append({"role": "system", "content": "You are a witty, sarcastic AI mentor."})

    history.append({"role":"user","content":chat_req.message})

    try:
        response = await client.chat.completions.create(
            messages = history,
            model = chat_req.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    bot_reply = response.choices[0].message.content

    history.append({"role": "assistant", "content": bot_reply})
    save_memory(history)
    
    return {"reply": bot_reply}


@app.delete("/chat")
async def clear_chat():
    save_memory([])
    return {"status": "Conversation history cleared."}
    
