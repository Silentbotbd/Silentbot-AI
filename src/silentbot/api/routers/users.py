from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ...core.db import db
from ...core.security import decode_token
from ...config import PRO_UNLOCK_CODE

router = APIRouter(prefix="/api/users", tags=["users"])

def get_current_user(x_token: Optional[str] = Header(None)):
    if not x_token: raise HTTPException(status_code=401)
    token = x_token.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload: raise HTTPException(status_code=401)
    return db.get_user_by_id(payload["sub"])

@router.get("/me")
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {k:v for k,v in user.items() if k != "password_hash"}

@router.post("/activate")
def activate_pro(code: str, user: Dict[str, Any] = Depends(get_current_user)):
    if code == PRO_UNLOCK_CODE:
        db.make_user_pro(user["id"])
        return {"status": "success", "is_pro": True}
    raise HTTPException(status_code=403, detail="Invalid Code")

@router.get("/sessions")
def get_sessions(user: Dict[str, Any] = Depends(get_current_user)):
    return db.list_sessions(user["id"])
