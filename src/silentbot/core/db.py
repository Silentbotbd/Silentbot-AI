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
        
        # Ensure Schema
        c.execute("""CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, email TEXT, password_hash TEXT, is_pro BOOLEAN DEFAULT 0, role TEXT DEFAULT 'user', req_count INTEGER DEFAULT 0, created_at REAL, last_login REAL, settings_json TEXT DEFAULT '{}')""")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, user_id TEXT, title TEXT, model TEXT DEFAULT 'auto', created_at REAL, updated_at REAL, is_archived BOOLEAN DEFAULT 0, FOREIGN KEY(user_id) REFERENCES users(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, tokens_count INTEGER DEFAULT 0, timestamp REAL, FOREIGN KEY(session_id) REFERENCES sessions(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, category TEXT, description TEXT, expert_prompt TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, fact TEXT, created_at REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, user_id TEXT, filename TEXT, content BLOB, file_type TEXT, created_at REAL)""")
        
        conn.commit()
        conn.close()
        self.seed_knowledge_force_update() # NEW: Force update knowledge
        self.seed_admin()

    def seed_admin(self):
        username = "Silentbotbd"
        if not self.get_user_by_username(username):
            hashed = get_password_hash("SilentBotBd2025 @@>!?")
            self.create_user(username, hashed, is_pro=True, role="admin", email="gmail.com_hrd")

    def seed_knowledge_force_update(self):
        """Upserts the Knowledge Base to ensure the latest 'Super-Intelligent' prompts are active."""
        conn = self._get_conn()
        c = conn.cursor()
        
        knowledge_base = [
            # --- WEB ---
            ("JavaScript", "Web", "Core", "You are a JavaScript Core Engineer. Focus on V8 runtime optimization, Event Loop nuances, ES2024 features, and memory leak prevention in React/Node.js."),
            ("TypeScript", "Web", "Typed", "You are a TypeScript Architect. Enforce strict typing, use Zod for validation, advanced Generics, and 'satisfies' operator. No 'any' type."),
            ("HTML", "Web", "Structure", "You are a Web Accessibility Expert. Ensure strict Semantic HTML5, WCAG 2.1 compliance, and perfect SEO structure."),
            ("CSS", "Web", "Style", "You are a CSS Artist. Use Modern CSS (Layers, Nesting, Container Queries), Tailwind best practices, and 60fps animations."),
            ("PHP", "Web", "Backend", "You are a Modern PHP Engineer. Use PHP 8.3+, strong typing, Attributes, Fiber coroutines, and Laravel 11 patterns."),

            # --- BACKEND/SYSTEMS ---
            ("Python", "Backend", "Systems", "You are a Python Principal Dev. Prioritize Pydantic models, FastAPI async patterns, type hinting (mypy), and PEP8 compliance."),
            ("Java", "Backend", "Enterprise", "You are a Java Champion. Focus on Virtual Threads (Project Loom), Spring Boot 3.2, GraalVM native images, and hexagonal architecture."),
            ("C++", "Systems", "Performance", "You are a C++ Systems Programmer. Use C++20/23 standards, Smart Pointers (no new/delete), Move Semantics, and compile-time optimization."),
            ("C#", "Systems", ".NET", "You are a .NET Architect. Use .NET 8, Minimal APIs, LINQ optimization, and Entity Framework Core performance tuning."),
            ("Go", "Systems", "Cloud", "You are a Go Expert. Focus on Idiomatic Go, advanced channel patterns, context propagation, and zero-allocation parsing."),
            ("Rust", "Systems", "Safety", "You are a Rustacean. Enforce strict ownership, use 'Anyhow' for error handling, async-std/tokio, and zero-cost abstractions."),

            # --- DATA & MOBILE ---
            ("SQL", "Data", "DB", "You are a DBA. Write high-performance SQL. Use CTEs, explain-analyze optimization, composite indexing, and normalized schemas."),
            ("Swift", "Mobile", "iOS", "You are an iOS Lead. Use SwiftUI with Observation framework, Swift 6 concurrency, and strictly adhere to Apple HIG."),
            ("Kotlin", "Mobile", "Android", "You are a Google Developer Expert. Use Jetpack Compose, Coroutines/Flow, Koin/Hilt dependency injection, and Clean Architecture."),
            ("R", "Data", "Stats", "You are a Data Scientist. Use Tidyverse, ggplot2 for publication-quality plots, and R-Markdown for reproducible research."),

            # --- SCRIPTING ---
            ("Bash", "Scripting", "Shell", "You are a DevOps Engineer. Write safe Bash (set -euo pipefail), use shellcheck standards, and avoid subshells where possible."),
            ("PowerShell", "Scripting", "Windows", "You are a Windows Admin. Use advanced Cmdlets, .NET interop, and Pester testing for scripts."),
            ("Perl", "Scripting", "Legacy", "You are a Perl Monk. Write maintainable Modern Perl, use strict/warnings, and CPAN best practices."),
            ("Ruby", "Scripting", "Dynamic", "You are a Rubyist. Focus on readability, Rails 7 conventions, Hotwire/Turbo interaction, and metaprogramming safety."),
            ("Lua", "Scripting", "Embed", "You are a Game Scripter. Optimize Lua for high-frequency loops (Roblox/Love2D), manage tables efficiently, and avoid garbage."),

            # --- OLDER/NICHE ---
            ("Fortran", "Niche", "HPC", "You are a Numerical Analyst. Optimize for vectorization, array slicing, and MPI parallel processing."),
            ("COBOL", "Niche", "Mainframe", "You are a Mainframe Expert. Focus on fixed-format layout, decimal precision, CICS transaction handling, and JCL."),
            ("Pascal", "Niche", "Edu", "You are a Structured Programming Expert. Emphasize type safety, modularity, and Delphi/Free Pascal extensions."),
            ("Assembly", "Niche", "LowLvl", "You are a Reverse Engineer. Optimize registers, understand pipeline stalls, SIMD instructions, and cache locality."),
            ("Haskell", "Niche", "Func", "You are a Lambda Theorist. Use Monad Transformers, point-free style, and lazy evaluation profiling."),
            ("Scala", "Niche", "JVM", "You are a Functional Architect. Use Scala 3 syntax, ZIO ecosystem, and Akka actor models."),
            ("Dart", "Niche", "Flutter", "You are a Flutter Engineer. Optimize widget rebuilds, use Riverpod/Bloc, and isolate logic in Isolate clusters.")
        ]

        # Use REPLACE to overwrite old prompt definitions with new smarter ones
        c.executemany("INSERT OR REPLACE INTO knowledge (key, category, description, expert_prompt) VALUES (?, ?, ?, ?)", knowledge_base)
        conn.commit()
        conn.close()

    # --- STANDARD METHODS (Preserved) ---
    def add_memory(self, uid, fact):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("INSERT INTO memory (user_id, fact, created_at) VALUES (?, ?, ?)", (uid, fact, time.time())); conn.commit(); conn.close()

    def get_memory(self, uid):
        conn = self._get_conn(); c = conn.cursor()
        c.execute("SELECT fact FROM memory WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (uid,)); rows = c.fetchall(); conn.close()
        return [r[0] for r in rows]

    def create_user(self, username, password_hash, is_pro=False, role="user", email=""):
        conn = self._get_conn(); c = conn.cursor(); uid = str(uuid.uuid4())
        try: c.execute("INSERT INTO users (id, username, email, password_hash, is_pro, role, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (uid, username, email, password_hash, 1 if is_pro else 0, role, time.time(), time.time())); conn.commit(); return self.get_user_by_id(uid)
        except: return None
        finally: conn.close()

    def get_user_by_username(self, u):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor(); c.execute("SELECT * FROM users WHERE username = ?", (u,)); row = c.fetchone(); conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, uid):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor(); c.execute("SELECT * FROM users WHERE id = ?", (uid,)); row = c.fetchone(); conn.close()
        return dict(row) if row else None
    
    def increment_request_count(self, uid):
        conn = self._get_conn(); c = conn.cursor(); c.execute("UPDATE users SET req_count = req_count + 1 WHERE id = ?", (uid,)); conn.commit(); conn.close()

    def make_user_pro(self, uid):
        conn = self._get_conn(); c = conn.cursor(); c.execute("UPDATE users SET is_pro = 1 WHERE id = ?", (uid,)); conn.commit(); conn.close()

    def create_session(self, uid, title="New Chat"):
        conn = self._get_conn(); c = conn.cursor(); sid = str(uuid.uuid4())
        c.execute("INSERT INTO sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", (sid, uid, title, time.time(), time.time())); conn.commit(); conn.close(); return sid

    def list_sessions(self, uid):
        conn = self._get_conn(); conn.row_factory = sqlite3.Row; c = conn.cursor(); c.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC", (uid,)); rows = c.fetchall(); conn.close()
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
