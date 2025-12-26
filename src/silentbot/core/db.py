import sqlite3
import pymysql
import time
import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from ..config import DATA_DIR, DB_TYPE, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

logger = logging.getLogger("silentbot.core.db")

class DatabaseManager:
    def __init__(self, db_name: str = "silentbot.db"):
        self.db_name = db_name
        self.db_path = os.path.join(DATA_DIR, db_name)
        self._init_db()

    def _get_conn(self):
        if DB_TYPE == "mysql":
            return pymysql.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()

        # Users Table
        users_table = """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                password_hash TEXT,
                role VARCHAR(50) DEFAULT 'user',
                is_pro INTEGER DEFAULT 0,
                req_count INTEGER DEFAULT 0,
                created_at DOUBLE,
                last_active DOUBLE
            )
        """
        
        # Sessions Table (Conversations)
        sessions_table = """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                title TEXT,
                created_at DOUBLE,
                updated_at DOUBLE
            )
        """

        # Messages Table
        messages_table = """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(255),
                role VARCHAR(50),
                content TEXT,
                timestamp DOUBLE
            )
        """ if DB_TYPE != "mysql" else """
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255),
                role VARCHAR(50),
                content TEXT,
                timestamp DOUBLE
            )
        """
        
        # Files Table
        files_table = """
            CREATE TABLE IF NOT EXISTS files (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255),
                filename TEXT,
                content LONGBLOB,
                file_type VARCHAR(100),
                created_at DOUBLE
            )
        """

        # Knowledge Table (Expert Modules)
        knowledge_table = """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                `key` VARCHAR(255),
                content TEXT,
                expert_prompt TEXT
            )
        """ if DB_TYPE != "mysql" else """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INT AUTO_INCREMENT PRIMARY KEY,
                `key` VARCHAR(255),
                content TEXT,
                expert_prompt TEXT
            )
        """

        # Memory Table (User Facts)
        memory_table = """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id VARCHAR(255),
                fact TEXT,
                created_at DOUBLE
            )
        """ if DB_TYPE != "mysql" else """
            CREATE TABLE IF NOT EXISTS memory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255),
                fact TEXT,
                created_at DOUBLE
            )
        """

        c.execute(users_table)
        c.execute(sessions_table)
        c.execute(messages_table)
        c.execute(files_table)
        c.execute(knowledge_table)
        c.execute(memory_table)

        conn.commit()
        conn.close()

    # --- User Management ---
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = %s" if DB_TYPE == "mysql" else "SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d['id'] = d['user_id'] # Alias for compatibility
            return d
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = %s" if DB_TYPE == "mysql" else "SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d['id'] = d['user_id']
            return d
        return None

    def create_user(self, username: str, password_hash: str, role: str = "user", is_pro: bool = False):
        user_id = str(uuid.uuid4())
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        try:
            sql = "INSERT INTO users (user_id, username, password_hash, role, is_pro, created_at, last_active) VALUES (%s, %s, %s, %s, %s, %s, %s)" if DB_TYPE == "mysql" else \
                  "INSERT INTO users (user_id, username, password_hash, role, is_pro, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(sql, (user_id, username, password_hash, role, 1 if is_pro else 0, now, now))
            conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
        finally:
            conn.close()
        return self.get_user_by_id(user_id)

    def update_user_login(self, user_id: str):
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        sql = "UPDATE users SET last_active = %s WHERE user_id = %s" if DB_TYPE == "mysql" else "UPDATE users SET last_active = ? WHERE user_id = ?"
        c.execute(sql, (now, user_id))
        conn.commit()
        conn.close()

    def update_user_pro(self, user_id: str, is_pro: bool):
        conn = self._get_conn()
        c = conn.cursor()
        sql = "UPDATE users SET is_pro = %s WHERE user_id = %s" if DB_TYPE == "mysql" else "UPDATE users SET is_pro = ? WHERE user_id = ?"
        c.execute(sql, (1 if is_pro else 0, user_id))
        conn.commit()
        conn.close()

    def make_user_pro(self, user_id: str):
        self.update_user_pro(user_id, True)

    def increment_request_count(self, user_id: str):
        conn = self._get_conn()
        c = conn.cursor()
        sql = "UPDATE users SET req_count = req_count + 1 WHERE user_id = %s" if DB_TYPE == "mysql" else "UPDATE users SET req_count = req_count + 1 WHERE user_id = ?"
        c.execute(sql, (user_id,))
        conn.commit()
        conn.close()

    # --- Session Management ---
    def create_session(self, user_id: str, title: str = "New Chat") -> str:
        session_id = str(uuid.uuid4())
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        sql = "INSERT INTO sessions (session_id, user_id, title, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)" if DB_TYPE == "mysql" else \
              "INSERT INTO sessions (session_id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)"
        c.execute(sql, (session_id, user_id, title, now, now))
        conn.commit()
        conn.close()
        return session_id

    def list_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        sql = "SELECT * FROM sessions WHERE user_id = %s ORDER BY updated_at DESC" if DB_TYPE == "mysql" else \
              "SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC"
        c.execute(sql, (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_message(self, session_id: str, role: str, content: str):
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        sql_msg = "INSERT INTO messages (session_id, role, content, timestamp) VALUES (%s, %s, %s, %s)" if DB_TYPE == "mysql" else \
                  "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)"
        c.execute(sql_msg, (session_id, role, content, now))
        
        sql_ses = "UPDATE sessions SET updated_at = %s WHERE session_id = %s" if DB_TYPE == "mysql" else \
                  "UPDATE sessions SET updated_at = ? WHERE session_id = ?"
        c.execute(sql_ses, (now, session_id))
        
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        sql = "SELECT role, content FROM messages WHERE session_id = %s ORDER BY id ASC LIMIT %s" if DB_TYPE == "mysql" else \
              "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?"
        c.execute(sql, (session_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    # --- Advanced Features ---
    def search_knowledge(self, query: str) -> List[Dict[str, str]]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM knowledge")
        rows = c.fetchall()
        conn.close()
        
        hits = []
        q_lower = query.lower()
        for r in rows:
            if r["key"].lower() in q_lower:
                hits.append(dict(r))
        return hits

    def get_memory(self, user_id: str) -> List[str]:
        conn = self._get_conn()
        if DB_TYPE != "mysql": conn.row_factory = sqlite3.Row
        c = conn.cursor()
        sql = "SELECT fact FROM memory WHERE user_id = %s ORDER BY created_at DESC LIMIT 5" if DB_TYPE == "mysql" else \
              "SELECT fact FROM memory WHERE user_id = ? ORDER BY created_at DESC LIMIT 5"
        c.execute(sql, (user_id,))
        rows = c.fetchall()
        conn.close()
        return [r["fact"] if DB_TYPE == "mysql" else r[0] for r in rows]

    def add_memory(self, user_id: str, fact: str):
        conn = self._get_conn()
        c = conn.cursor()
        sql = "INSERT INTO memory (user_id, fact, created_at) VALUES (%s, %s, %s)" if DB_TYPE == "mysql" else \
              "INSERT INTO memory (user_id, fact, created_at) VALUES (?, ?, ?)"
        c.execute(sql, (user_id, fact, time.time()))
        conn.commit()
        conn.close()

# Global DB Instance
db = DatabaseManager()