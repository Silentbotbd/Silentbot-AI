from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from ..config import PROJECT_NAME, VERSION, UI_DIR
from .routers import auth, chat, users
import os

app = FastAPI(title=PROJECT_NAME, version=VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(users.router)

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    p = os.path.join(UI_DIR, "index.html")
    with open(p, "r", encoding="utf-8") as f: return f.read()
