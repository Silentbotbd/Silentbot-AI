import sqlite3
import time
import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from ..config import DATA_DIR
from .security import get_password_hash

logger = logging.getLogger("silentbot.core.db")

class DatabaseManager:
    def __init__(self, db_name: str = "silentbot_pro_v2.db"):
        self.db_path = os.path.join(DATA_DIR, db_name)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, email TEXT, password_hash TEXT, is_pro BOOLEAN DEFAULT 0, role TEXT DEFAULT 'user', req_count INTEGER DEFAULT 0, created_at REAL, last_login REAL, settings_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, model TEXT DEFAULT 'auto', created_at REAL, updated_at REAL, is_archived BOOLEAN DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, tokens_count INTEGER DEFAULT 0, timestamp REAL, FOREIGN KEY(session_id) REFERENCES sessions(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, category TEXT, description TEXT, expert_prompt TEXT)""")
        conn.commit()
        conn.close()
        self.seed_knowledge()
        self.seed_admin()

    def seed_admin(self):
        username = "Silentbotbd"
        password = "SilentBotBd2025 @@>!?"
        if not self.get_user_by_username(username):
            hashed = get_password_hash(password)
            self.create_user(username, hashed, is_pro=True, role="admin", email="gmail.com_hrd")

    def seed_knowledge(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT count(*) FROM knowledge")
        if c.fetchone()[0] > 0:
            conn.close()
            return
        languages = [
            ("JavaScript", "Web", "Core", "Expert in React, Node, etc."),
            ("Python", "Backend", "AI", "Expert in FastAPI, ML, etc."),
            ("Rust", "Systems", "Performance", "Expert in memory safety."),
            ("Go", "Systems", "Scalability", "Expert in concurrency.")
        ]
        c.executemany("INSERT OR IGNORE INTO knowledge (key, category, description, expert_prompt) VALUES (?, ?, ?, ?)", languages)
        conn.commit()
        conn.close()

    def create_user(self, username: str, password_hash: str, is_pro: bool = False, role: str = "user", email: str = ""):
        conn = self._get_conn()
        c = conn.cursor()
        uid = str(uuid.uuid4())
        now = time.time()
        try:
            c.execute("INSERT INTO users (id, username, email, password_hash, is_pro, role, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (uid, username, email, password_hash, 1 if is_pro else 0, role, now, now))
            conn.commit()
            return self.get_user_by_id(uid)
        except: return None
        finally: conn.close()

    def get_user_by_username(self, u: str):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (u,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, uid: str):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (uid,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def increment_request_count(self, uid: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET req_count = req_count + 1 WHERE id = ?", (uid,))
        conn.commit()
        conn.close()

    def make_user_pro(self, uid: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET is_pro = 1 WHERE id = ?", (uid,))
        conn.commit()
        conn.close()

    def create_session(self, uid: str, title: str = "New Chat"):
        conn = self._get_conn()
        c = conn.cursor()
        sid = str(uuid.uuid4())
        now = time.time()
        c.execute("INSERT INTO sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", (sid, uid, title, now, now))
        conn.commit()
        conn.close()
        return sid

    def list_sessions(self, uid: str):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC", (uid,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_message(self, sid: str, role: str, content: str):
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)", (sid, role, content, now))
        c.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, sid))
        conn.commit()
        conn.close()

    def get_history(self, sid: str, limit: int = 100):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (sid,))
        rows = c.fetchall()
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows][-limit:]

    def search_knowledge(self, query: str):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        w = f"%{query}%"
        c.execute("SELECT * FROM knowledge WHERE key LIKE ? OR description LIKE ? OR category LIKE ?", (w, w, w))
        rows = c.fetchall()
        conn.close()
        return [{"key": r["key"], "expert_prompt": r["expert_prompt"]} for r in rows]

db = DatabaseManager()
