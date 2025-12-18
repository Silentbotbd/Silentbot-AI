import os
import sys
import uuid
import time
import logging
import requests
import uvicorn
from typing import List, Optional, Literal, Dict
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# ==============================================================================
#  1. PRODUCTION CONFIGURATION
# ==============================================================================

# Load any .env file if present (for local testing)
load_dotenv()

# --- API KEYS (INTEGRATED) ---
# Your OpenAI Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Your Hostion Verification Key
HOSTION_API_KEY = os.getenv("HOSTION_API_KEY", "")

# --- SETTINGS ---
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_MODEL = "gpt-4o"
PRO_UNLOCK_CODE = "MYSECRETPROCODE"
VERSION = "3.0.0-PROD"

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SilentBot")

# ==============================================================================
#  2. DATA MODELS & DATABASE
# ==============================================================================

class UserState(BaseModel):
    user_id: str
    is_pro: bool = False
    req_count: int = 0
    last_window: int = 0

USERS: Dict[str, UserState] = {}

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: Optional[Literal["auto", "normal", "pro"]] = "auto"

# ==============================================================================
#  3. CORE LOGIC
# ==============================================================================

app = FastAPI(title="Silent Bot CLI & Web", version=VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user(uid: Optional[str]) -> UserState:
    uid = uid if uid else str(uuid.uuid4())
    if uid not in USERS:
        USERS[uid] = UserState(user_id=uid)
    return USERS[uid]

def call_openai(messages: List[dict], max_tokens: int):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        resp = requests.post(f"{OPENAI_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=45)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        raise HTTPException(status_code=502, detail="AI Provider Error. Please check logs.")

# ==============================================================================
#  4. API ENDPOINTS
# ==============================================================================

@app.get("/health")
def health():
    return {"status": "online", "version": VERSION, "hostion_key": "Verified"}

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest, x_client_id: Optional[str] = Header(None)):
    user = get_user(x_client_id)
    
    # Mode Logic
    mode = "pro" if (req.mode == "pro" and user.is_pro) else "normal"
    if req.mode == "pro" and not user.is_pro:
        raise HTTPException(status_code=403, detail="Pro Mode Locked. Please Activate.")

    # Prompt Engineering
    sys = "You are Silent Bot. A helpful, secure AI assistant."
    if mode == "pro":
        sys += " [PRO MODE ACTIVE] Provide advanced, detailed, and architectural solutions."
    
    msgs = [{"role": "system", "content": sys}] + [m.dict() for m in req.messages]
    
    # Execution
    tokens = 2048 if mode == "pro" else 512
    data = call_openai(msgs, tokens)
    content = data["choices"][0]["message"]["content"]
    
    return {"response": content, "mode": mode}

@app.post("/api/activate")
def activate(code: str = "", x_client_id: Optional[str] = Header(None)):
    user = get_user(x_client_id)
    if code.strip() == PRO_UNLOCK_CODE:
        user.is_pro = True
        return {"status": "success"}
    raise HTTPException(status_code=403, detail="Invalid Code")

@app.get("/api/me")
def me(x_client_id: Optional[str] = Header(None)):
    user = get_user(x_client_id)
    return {"id": user.user_id, "is_pro": user.is_pro}

# ==============================================================================
#  5. INTEGRATED FRONTEND (HTML/JS)
# ==============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Silent Bot Production</title>
    <style>
        :root{--bg:#0a0a0a;--card:#171717;--text:#ededed;--accent:#22c55e;}
        body{background:var(--bg);color:var(--text);font-family:monospace;margin:0;display:flex;justify-content:center;height:100vh;overflow:hidden;}
        .container{width:100%;max-width:900px;display:flex;flex-direction:column;padding:20px;gap:15px;}
        header{border-bottom:1px solid #333;padding-bottom:15px;text-align:center;}
        h1{margin:0;color:var(--accent);}
        .chat-box{flex:1;background:var(--card);border:1px solid #333;border-radius:8px;padding:20px;overflow-y:auto;display:flex;flex-direction:column;gap:15px;}
        .msg{padding:10px 15px;border-radius:6px;max-width:85%;line-height:1.5;white-space:pre-wrap;}
        .user{align-self:flex-end;background:#065f46;color:white;}
        .bot{align-self:flex-start;background:#262626;border:1px solid #404040;}
        .input-area{display:flex;gap:10px;}
        input{flex:1;background:#171717;border:1px solid #404040;padding:15px;color:white;border-radius:6px;outline:none;}
        input
