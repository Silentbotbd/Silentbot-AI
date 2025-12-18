from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Dict, Any
from ...core.db import db
from ...core.security import decode_token
from fastapi import Header

router = APIRouter(prefix="/api/files", tags=["files"])

def get_current_user(x_client_id: str = Header(None)):
    if not x_client_id: return None
    return db.get_user_by_id(x_client_id) or db.create_user(f"guest_{x_client_id[:8]}", "guest", role="guest")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), x_client_id: str = Header(None)):
    if not x_client_id:
        raise HTTPException(status_code=400, detail="Missing Client ID")
    
    content = await file.read()
    # In a real production app, we might store this in S3 or local disk.
    # For this SQLite setup, we'll store metadata or small content in DB, or just acknowledge it.
    
    # Store in DB (Schema supports files)
    import uuid
    import time
    file_id = str(uuid.uuid4())
    
    conn = db._get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO files (id, user_id, filename, content, file_type, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (file_id, x_client_id, file.filename, content, file.content_type, time.time()))
    conn.commit()
    conn.close()
    
    return {"filename": file.filename, "status": "uploaded", "id": file_id}
