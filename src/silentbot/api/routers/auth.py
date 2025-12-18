from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from ...core.db import db
from ...core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserAuth(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register", response_model=Token)
def register(user_data: UserAuth):
    if db.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = get_password_hash(user_data.password)
    user = db.create_user(user_data.username, hashed)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
        
    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=Token)
def login(user_data: UserAuth):
    user = db.get_user_by_username(user_data.username)
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    db.update_user_login(user["id"])
    token = create_access_token({"sub": user["id"]})
    return {"access_token": token, "token_type": "bearer", "user": user}
