from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
import re
from ...core.db import db
from ...core.agent import Agent
from ...core.security import decode_token

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: Optional[Literal["auto", "normal", "pro"]] = "auto"
    session_id: Optional[str] = None

def get_current_user(x_token: Optional[str] = Header(None), x_client_id: Optional[str] = Header(None)):
    if x_token:
        token = x_token.replace("Bearer ", "")
        payload = decode_token(token)
        if payload:
            return db.get_user_by_id(payload["sub"])
            
    if x_client_id:
        username = f"guest_{x_client_id[:8]}"
        user = db.get_user_by_username(username)
        if not user:
            user = db.create_user(username, "guest_pass", role="guest")
        return user
        
    return None

def detect_code_request(text: str) -> bool:
    keywords = ["code", "script", "function", "class", "debug", "fix", "html", "css", "python", "javascript"]
    text_lower = text.lower()
    return any(k in text_lower for k in keywords)

@router.post("/", summary="Send a message")
def chat_endpoint(req: ChatRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user["id"] if user else "anonymous"
    is_pro = user.get("is_pro", False) if user else False
    req_count = user.get("req_count", 0) if user else 0
    
    if not is_pro and req_count >= 30:
        raise HTTPException(status_code=402, detail="LIMIT_REACHED")

    target_mode = req.mode
    if target_mode == "auto":
        target_mode = "pro" if is_pro else "normal"

    if target_mode == "pro" and not is_pro:
        raise HTTPException(status_code=403, detail="Pro Mode Locked.")

    last_msg = req.messages[-1].content if req.messages else ""
    session_id = req.session_id
    if not session_id:
        session_id = db.create_session(user_id, title="New Chat")

    db.add_message(session_id, "user", last_msg)
    if user:
        db.increment_request_count(user_id)

    limit = 1000 if is_pro else 20
    history_dicts = db.get_history(session_id, limit=limit)
    
    agent = Agent(mode=target_mode)
    
    try:
        instr = ""
        if target_mode == "normal" and detect_code_request(last_msg):
            instr = " [SYSTEM: NORMAL mode. REFUSE code generation. Ask to upgrade.]"

        result = agent.run(last_msg + instr, history_dicts)
        db.add_message(session_id, "assistant", result["response"])
        
        return {
            "response": result["response"],
            "session_id": session_id,
            "steps": result.get("steps", []),
            "tokens": result.get("tokens", 0),
            "usage": req_count + 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(session_id: str):
    return db.get_history(session_id)

@router.get("/sessions")
def list_sessions(user: Dict[str, Any] = Depends(get_current_user)):
    if not user:
        return []
    return db.list_sessions(user["id"])
