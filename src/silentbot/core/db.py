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
    def __init__(self, db_name: str = "silentbot_ultimate_v1.db"):
        self.db_path = os.path.join(DATA_DIR, db_name)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()
        
        # Core Tables
        c.execute("""CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, email TEXT, password_hash TEXT, is_pro BOOLEAN DEFAULT 0, role TEXT DEFAULT 'user', req_count INTEGER DEFAULT 0, created_at REAL, last_login REAL, settings_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, model TEXT DEFAULT 'auto', created_at REAL, updated_at REAL, is_archived BOOLEAN DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, tokens_count INTEGER DEFAULT 0, timestamp REAL, FOREIGN KEY(session_id) REFERENCES sessions(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, category TEXT, description TEXT, expert_prompt TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, fact TEXT, created_at REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, content BLOB, file_type TEXT, created_at REAL)""")
        
        conn.commit()
        conn.close()
        self.seed_knowledge()
        self.seed_admin()

    def seed_admin(self):
        username = "Silentbotbd"
        if not self.get_user_by_username(username):
            hashed = get_password_hash("SilentBotBd2025 @@>!?")
            self.create_user(username, hashed, is_pro=True, role="admin", email="gmail.com_hrd")

    def seed_knowledge(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT count(*) FROM knowledge")
        # Only seed if fewer than 50 entries (implies old DB)
        if c.fetchone()[0] > 50:
            conn.close()
            return
        
        knowledge_base = [
            # --- WRITING ASSISTANCE ---
            ("Essays", "Writing", "Academic Structure", "Expert in academic structure, thesis statements, arguments, and citations (APA/MLA)."),
            ("Creative Writing", "Writing", "Storytelling", "Expert in narrative arcs, character development, dialogue, and vivid imagery."),
            ("Business Writing", "Writing", "Professional", "Expert in concise, persuasive business communication, proposals, and executive summaries."),
            ("Technical Writing", "Writing", "Documentation", "Expert in clear, step-by-step technical manuals, API docs, and standard operating procedures."),
            
            # --- EDITING ---
            ("Grammar", "Editing", "Correction", "Expert in strict grammar rules, punctuation, and syntax optimization."),
            ("Tone", "Editing", "Adjustment", "Expert in tone shifting (e.g., casual to formal, aggressive to diplomatic)."),
            ("Rewriting", "Editing", "Paraphrasing", "Expert in rephrasing for clarity, brevity, and impact while retaining meaning."),

            # --- PROFESSIONAL ---
            ("Resume", "Professional", "CV Optimization", "Expert in ATS-friendly formatting, action verbs, and highlighting achievements."),
            ("Cover Letter", "Professional", "Job Application", "Expert in persuasive, personalized cover letters that match job descriptions."),
            ("Social Media", "Professional", "Engagement", "Expert in hooks, viral structures, and platform-specific formatting (LinkedIn/Twitter)."),

            # --- PROGRAMMING: WEB ---
            ("JavaScript", "Web", "Frontend/Backend", "Expert in ES6+, Async/Await, DOM, React ecosystem, and Node.js performance."),
            ("TypeScript", "Web", "Strict Typing", "Expert in Interfaces, Generics, Utility Types, and strict configuration."),
            ("HTML", "Web", "Structure", "Expert in Semantic HTML5, Accessibility (ARIA), and SEO best practices."),
            ("CSS", "Web", "Styling", "Expert in Flexbox, Grid, Tailwind, Animations, and responsive design."),
            ("PHP", "Web", "Backend", "Expert in Modern PHP 8.2, Laravel, Symfony, and Composer."),

            # --- PROGRAMMING: SYSTEMS ---
            ("Python", "Backend", "General Purpose", "Expert in FastAPI, Django, Data Science (Pandas/NumPy), and Automation."),
            ("Java", "Backend", "Enterprise", "Expert in Spring Boot, JVM Internals, Multithreading, and Design Patterns."),
            ("C++", "Systems", "Performance", "Expert in Memory Management, Pointers, STL, and Game Development (Unreal)."),
            ("C#", "Systems", "Enterprise/Game", "Expert in .NET Core, LINQ, Async patterns, and Unity 3D."),
            ("Go", "Systems", "Cloud Native", "Expert in Goroutines, Channels, Microservices, and gRPC."),
            ("Rust", "Systems", "Safety", "Expert in Ownership, Borrowing, Lifetimes, and Systems Programming."),

            # --- DATA & MOBILE ---
            ("SQL", "Data", "Database", "Expert in Complex Joins, Window Functions, Indexing, and Normalization."),
            ("Swift", "Mobile", "iOS", "Expert in SwiftUI, Combine, XCode, and iOS Design Guidelines."),
            ("Kotlin", "Mobile", "Android", "Expert in Jetpack Compose, Coroutines, and Android SDK."),
            ("R", "Data", "Statistics", "Expert in Statistical Modeling, ggplot2, and Data Visualization."),

            # --- SCRIPTING ---
            ("Bash", "Scripting", "Linux Shell", "Expert in Shell Scripting, Cron, Pipes, and System Admin."),
            ("PowerShell", "Scripting", "Windows", "Expert in Cmdlets, Active Directory, and Windows Automation."),
            ("Perl", "Scripting", "Text Processing", "Expert in Regex and Legacy System maintenance."),
            ("Ruby", "Scripting", "Web/Scripting", "Expert in Rails, Metaprogramming, and clean syntax."),
            ("Lua", "Scripting", "Embedded", "Expert in Game Scripting (Roblox/WoW) and lightweight embedding."),

            # --- NICHE ---
            ("Fortran", "Niche", "Scientific", "Expert in High-Performance Computing and Numerical Analysis."),
            ("COBOL", "Niche", "Legacy Business", "Expert in Mainframe systems and Transactional Processing."),
            ("Assembly", "Niche", "Low Level", "Expert in x86/ARM Architecture, Registers, and Opcode optimization."),
            ("Haskell", "Niche", "Functional", "Expert in Pure Functions, Monads, and Type Theory."),
            ("Dart", "Niche", "Cross-Platform", "Expert in Flutter Widget tree and State Management."),
            ("Scala", "Niche", "JVM Functional", "Expert in Akka, Spark, and Functional/OOP hybrid patterns.")
        ]

        c.executemany("INSERT OR IGNORE INTO knowledge (key, category, description, expert_prompt) VALUES (?, ?, ?, ?)", knowledge_base)
        conn.commit()
        conn.close()

    # --- MEMORY SYSTEM ---
    def add_memory(self, user_id: str, fact: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO memory (user_id, fact, created_at) VALUES (?, ?, ?)", (user_id, fact, time.time()))
        conn.commit()
        conn.close()

    def get_memory(self, user_id: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT fact FROM memory WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]

    # --- STANDARD METHODS ---
    def create_user(self, username, password_hash, is_pro=False, role="user", email=""):
        conn = self._get_conn()
        c = conn.cursor()
        uid = str(uuid.uuid4())
        try:
            c.execute("INSERT INTO users (id, username, email, password_hash, is_pro, role, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (uid, username, email, password_hash, 1 if is_pro else 0, role, time.time(), time.time()))
            conn.commit()
            return self.get_user_by_id(uid)
        except: return None
        finally: conn.close()

    def get_user_by_username(self, u):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (u,)); row = c.fetchone(); conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, uid):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (uid,)); row = c.fetchone(); conn.close()
        return dict(row) if row else None
    
    def increment_request_count(self, uid):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("UPDATE users SET req_count = req_count + 1 WHERE id = ?", (uid,)); conn.commit(); conn.close()

    def make_user_pro(self, uid):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("UPDATE users SET is_pro = 1 WHERE id = ?", (uid,)); conn.commit(); conn.close()

    def create_session(self, uid, title="New Chat"):
        conn = self._get_conn(); c = conn.cursor(); sid = str(uuid.uuid4())
        c.execute("INSERT INTO sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", (sid, uid, title, time.time(), time.time()))
        conn.commit(); conn.close(); return sid

    def list_sessions(self, uid):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC", (uid,)); rows = c.fetchall(); conn.close()
        return [dict(r) for r in rows]

    def add_message(self, sid, role, content):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)", (sid, role, content, time.time()))
        c.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (time.time(), sid)); conn.commit(); conn.close()

    def get_history(self, sid, limit=100):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (sid,)); rows = c.fetchall(); conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows][-limit:]

    def search_knowledge(self, query):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor(); w = f"%{query}%"
        c.execute("SELECT * FROM knowledge WHERE key LIKE ? OR description LIKE ? OR category LIKE ?", (w, w, w)); rows = c.fetchall(); conn.close()
        return [{"key": r["key"], "expert_prompt": r["expert_prompt"]} for r in rows]

db = DatabaseManager()