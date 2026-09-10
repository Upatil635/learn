"""Persist AI generations so chapters and questions are not regenerated."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from config import Config


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


class AiCache:
    KIND_CHAPTER = "chapter_pack"
    KIND_ASK = "ask"
    KIND_QUIZ = "quiz"

    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.APP_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    chapter TEXT NOT NULL DEFAULT '',
                    model TEXT NOT NULL,
                    prompt_key TEXT NOT NULL DEFAULT '',
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(kind, subject, chapter, model, prompt_key)
                )
                """
            )
            conn.commit()

    @staticmethod
    def model_id() -> str:
        return f"{Config.llm_provider()}:{Config.llm_model()}"

    def get(
        self,
        kind: str,
        subject: str,
        chapter: str = "",
        prompt_key: str = "",
        model: str = None,
    ) -> Optional[Dict[str, Any]]:
        model = model or self.model_id()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT payload_json, created_at FROM ai_generations
                WHERE kind = ? AND subject = ? AND chapter = ? AND model = ? AND prompt_key = ?
                """,
                (kind, subject, chapter or "", model, _norm(prompt_key)),
            ).fetchone()
        if not row:
            return None
        payload = json.loads(row["payload_json"])
        payload["_cached"] = True
        payload["_cached_at"] = row["created_at"]
        return payload

    def put(
        self,
        kind: str,
        subject: str,
        payload: Dict[str, Any],
        chapter: str = "",
        prompt_key: str = "",
        model: str = None,
    ) -> Dict[str, Any]:
        model = model or self.model_id()
        now = datetime.now(timezone.utc).isoformat()
        to_store = {k: v for k, v in payload.items() if not str(k).startswith("_")}
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO ai_generations (kind, subject, chapter, model, prompt_key, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(kind, subject, chapter, model, prompt_key)
                DO UPDATE SET payload_json = excluded.payload_json, created_at = excluded.created_at
                """,
                (
                    kind,
                    subject,
                    chapter or "",
                    model,
                    _norm(prompt_key),
                    json.dumps(to_store),
                    now,
                ),
            )
            conn.commit()
        to_store["_cached"] = False
        to_store["_cached_at"] = now
        return to_store
