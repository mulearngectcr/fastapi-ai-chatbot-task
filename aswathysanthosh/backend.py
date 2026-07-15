import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import AsyncGroq
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from duckduckgo_search import DDGS

load_dotenv()

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Groq Client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
MEMORY_FILE = "memory.json"

class ChatRequest(BaseModel):
    message: str
    model: str = "llama-3.1-8b-instant"

def search_web(query: str, max_results: int = 3) -> str:
    """Searches the live web using DuckDuckGo to pull real-time summaries."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            if not results:
                return "No real-time search results found."
            
            context = "Real-time search results from the web:\n"
            for r in results:
                context += f"- Title: {r['title']}\n  Snippet: {r['body']}\n\n"
            return context
    except Exception as e:
        return f"Failed to fetch live data: {str(e)}"

def load_memory():
    """Loads chat history from the local JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_memory(history):
    """Saves chat history to the local JSON file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

@app.post("/chat")
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    history = load_memory()
    
    # Get current live date dynamically
    today_date = datetime.now().strftime("%B %d, %Y")

    # Inject a friendly system prompt with the correct context date if history is empty
    if not history:
        system_prompt = (
            f"You are a friendly, helpful, and supportive AI assistant. "
            f"Today's date is strictly {today_date}. You have access to real-time search summaries "
            f"provided alongside user questions to answer queries beyond your training cutoff."
        )
        history.append({"role": "system", "content": system_prompt})

    user_message = chat_req.message
    lower_msg = user_message.lower()
    
    # Keywords that indicate the user wants current or real-time info
    search_keywords = ["today", "current", "latest", "news", "2026", "who is", "match", "score", "weather", "live"]
    
    # Check if we need to search the web
    if any(keyword in lower_msg for keyword in search_keywords):
        live_search_context = search_web(user_message)
        formatted_message = f"{live_search_context}\nUser Question: {user_message}"
    else:
        formatted_message = user_message

    # Append to working history for the API call
    history.append({"role": "user", "content": formatted_message})

    try:
        response = await client.chat.completions.create(
            messages=history,
            model=chat_req.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    bot_reply = response.choices[0].message.content

    # Revert the appended context back to the clean user message to keep saved logs tidy
    history[-1]["content"] = user_message
    history.append({"role": "assistant", "content": bot_reply})
    
    save_memory(history)
    
    return {"reply": bot_reply}

@app.delete("/chat")
async def clear_chat():
    """Clears the chat memory history entirely."""
    save_memory([])
    return {"status": "Conversation history cleared."}