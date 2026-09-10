"""SQLite user accounts and quiz history."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

VALID_THEMES = ("system", "light", "dark")


class UserStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.APP_DB_PATH
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        import os

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    theme TEXT NOT NULL DEFAULT 'system',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    chapter TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    num_questions INTEGER NOT NULL,
                    attempt_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
            conn.commit()

    def create_user(self, username: str, password: str) -> Dict[str, Any]:
        username = (username or "").strip()
        if not username:
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password or "") < 8:
            raise ValueError("Password must be at least 8 characters")

        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash, theme, created_at) VALUES (?, ?, ?, ?)",
                    (username, generate_password_hash(password, method="pbkdf2:sha256"), "system", now),
                )
                conn.commit()
                return {
                    "id": cur.lastrowid,
                    "username": username,
                    "theme": "system",
                }
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{username}' already exists")

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, theme FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()
        if not row or not check_password_hash(row["password_hash"], password):
            return None
        return {"id": row["id"], "username": row["username"], "theme": row["theme"]}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, theme FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "username": row["username"], "theme": row["theme"]}

    def set_theme(self, user_id: int, theme: str) -> Dict[str, Any]:
        if theme not in VALID_THEMES:
            raise ValueError("Theme must be system, light, or dark")
        with self._connect() as conn:
            conn.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
            conn.commit()
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def save_attempt(
        self,
        user_id: int,
        subject: str,
        chapter: str,
        score: int,
        num_questions: int,
        attempt: Dict[str, Any],
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO quiz_attempts
                    (user_id, subject, chapter, score, num_questions, attempt_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    subject,
                    chapter,
                    int(score),
                    int(num_questions),
                    json.dumps(attempt),
                    now,
                ),
            )
            conn.commit()
            attempt_id = cur.lastrowid
        return self.get_attempt(user_id, attempt_id)

    def list_attempts(self, user_id: int) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, subject, chapter, score, num_questions, created_at
                FROM quiz_attempts
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_attempt(self, user_id: int, attempt_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, subject, chapter, score, num_questions, attempt_json, created_at
                FROM quiz_attempts
                WHERE id = ? AND user_id = ?
                """,
                (attempt_id, user_id),
            ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["attempt"] = json.loads(data.pop("attempt_json"))
        return data

    @staticmethod
    def issue_token(user: Dict[str, Any]) -> str:
        Config.validate_jwt()
        payload = {
            "sub": str(user["id"]),
            "username": user["username"],
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }
        return jwt.encode(payload, Config.jwt_secret(), algorithm="HS256")

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        Config.validate_jwt()
        return jwt.decode(token, Config.jwt_secret(), algorithms=["HS256"])
