"""LearnEasy Flask Backend API"""
import sys
from functools import wraps
from pathlib import Path

import jwt
from flask import Flask, g, jsonify, redirect, request
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config
from src.ai_cache import AiCache
from src.gemini_handler import GeminiHandler
from src.ingester import DocumentIngester
from src.rag_retriever import RAGRetriever
from src.user_store import UserStore
from src.vector_db import get_vector_db

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

retriever = RAGRetriever()
gemini = GeminiHandler()
vector_db = get_vector_db()
users = UserStore()
ai_cache = AiCache()
FRONTEND_URL = "http://localhost:3000"


@app.route("/")
def root():
    """Browsers hitting the API port are sent to the React app."""
    return redirect(FRONTEND_URL)


@app.route("/api")
def api_index():
    return jsonify({
        "name": "LearnEasy API",
        "status": "ok",
        "app": FRONTEND_URL,
        "health": "/api/health",
    })


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        token = header[7:].strip()
        try:
            payload = UserStore.decode_token(token)
            user = users.get_user(int(payload["sub"]))
            if not user:
                return jsonify({"success": False, "error": "Unauthorized"}), 401
            g.user = user
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "error": "Token expired"}), 401
        except (jwt.InvalidTokenError, KeyError, ValueError):
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper


@app.route("/api/health", methods=["GET"])
def health():
    try:
        stats = vector_db.get_collection_stats()
        return jsonify({
            "status": "healthy",
            "database": {
                "total_documents": stats["total_documents"],
                "collection_name": stats["collection_name"],
            },
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = users.authenticate(username, password)
    if not user:
        return jsonify({"success": False, "error": "Invalid username or password"}), 401
    token = UserStore.issue_token(user)
    return jsonify({"success": True, "token": token, "user": user})


@app.route("/api/auth/me", methods=["GET"])
@require_auth
def me():
    return jsonify({"success": True, "user": g.user})


@app.route("/api/auth/me", methods=["PATCH"])
@require_auth
def update_me():
    data = request.get_json() or {}
    theme = data.get("theme")
    try:
        user = users.set_theme(g.user["id"], theme)
        return jsonify({"success": True, "user": user})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/setup", methods=["POST"])
@require_auth
def setup():
    try:
        ingester = DocumentIngester()
        ingester.reingest_documents()
        stats = vector_db.get_collection_stats()
        return jsonify({
            "success": True,
            "message": f"Ingested {stats['total_documents']} documents",
            "stats": stats,
        })
    except Exception as e:
        app.logger.error(f"Setup error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
@require_auth
def query():
    try:
        data = request.get_json() or {}
        query_text = data.get("query", "")
        top_k = data.get("top_k", 5)
        subject = data.get("subject")
        if not query_text:
            return jsonify({"error": "Query text required"}), 400
        results = retriever.retrieve_context(query_text, top_k=top_k, subject_filter=subject)
        return jsonify({
            "success": True,
            "query": query_text,
            "total_retrieved": results["total_retrieved"],
            "documents": results["retrieved_documents"],
        })
    except Exception as e:
        app.logger.error(f"Query error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/quiz", methods=["POST"])
@require_auth
def generate_quiz():
    try:
        data = request.get_json() or {}
        topic = data.get("topic", "")
        difficulty = data.get("difficulty", "medium")
        num_questions = data.get("num_questions", 5)
        subject = data.get("subject")
        if not topic:
            return jsonify({"error": "Topic required"}), 400
        force = bool(data.get("force"))
        cache_key = f"{topic}|{difficulty}|{num_questions}|{subject or ''}"
        if not force:
            hit = ai_cache.get(AiCache.KIND_QUIZ, subject or "", "", cache_key)
            if hit:
                return jsonify({
                    "success": True,
                    "topic": topic,
                    "difficulty": difficulty,
                    "quiz": hit.get("quiz", []),
                    "num_questions": hit.get("num_questions", 0),
                    "cached": True,
                    "cached_at": hit.get("_cached_at"),
                })
        results = retriever.retrieve_context(topic, subject_filter=subject)
        context = results.get("context", "")
        if not context:
            return jsonify({"error": "No relevant content found"}), 404
        quiz_result = gemini.generate_quiz(context, num_questions, difficulty)
        if not quiz_result.get("success"):
            return jsonify({"success": False, "error": quiz_result.get("error")}), 500
        stored = ai_cache.put(
            AiCache.KIND_QUIZ,
            subject or "",
            {
                "quiz": quiz_result.get("quiz", []),
                "num_questions": quiz_result.get("num_questions", 0),
            },
            prompt_key=cache_key,
        )
        return jsonify({
            "success": True,
            "topic": topic,
            "difficulty": difficulty,
            "quiz": stored.get("quiz", []),
            "num_questions": stored.get("num_questions", 0),
            "cached": False,
        })
    except Exception as e:
        app.logger.error(f"Quiz generation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ask", methods=["POST"])
@require_auth
def ask_question():
    try:
        data = request.get_json() or {}
        question = data.get("question", "")
        subject = data.get("subject")
        if not question:
            return jsonify({"error": "Question required"}), 400
        force = bool(data.get("force"))
        if not force:
            hit = ai_cache.get(AiCache.KIND_ASK, subject or "", "", question)
            if hit:
                return jsonify({
                    "success": True,
                    "question": question,
                    "answer": hit.get("answer", ""),
                    "sources": hit.get("sources", 0),
                    "cached": True,
                    "cached_at": hit.get("_cached_at"),
                })
        results = retriever.retrieve_context(question, subject_filter=subject)
        context = results.get("context", "")
        answer_result = gemini.answer_question(context, question)
        if not answer_result.get("success"):
            return jsonify({"success": False, "error": answer_result.get("error")}), 500
        stored = ai_cache.put(
            AiCache.KIND_ASK,
            subject or "",
            {"answer": answer_result.get("answer", ""), "sources": len(results.get("retrieved_documents", []))},
            prompt_key=question,
        )
        return jsonify({
            "success": True,
            "question": question,
            "answer": stored.get("answer", ""),
            "sources": stored.get("sources", 0),
            "cached": False,
        })
    except Exception as e:
        app.logger.error(f"Answer error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
@require_auth
def get_status():
    try:
        stats = vector_db.get_collection_stats()
        results = vector_db.collection.get(limit=50000)
        subjects = set()
        chapters = set()
        for metadata in results.get("metadatas", []):
            subjects.add(metadata.get("subject", "Unknown"))
            chapters.add(metadata.get("chapter", "Unknown"))
        return jsonify({
            "success": True,
            "database": {
                "total_documents": stats["total_documents"],
                "total_subjects": len(subjects),
                "total_chapters": len(chapters),
                "collection_name": stats["collection_name"],
                "path": stats["path"],
            },
            "subjects": sorted(list(subjects)),
        })
    except Exception as e:
        app.logger.error(f"Status error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/learn/subjects", methods=["GET"])
@require_auth
def learn_get_subjects():
    try:
        results = vector_db.collection.get(limit=50000)
        subjects = {}
        for metadata in results.get("metadatas", []):
            subject = metadata.get("subject", "Unknown")
            if subject not in subjects:
                subjects[subject] = {
                    "name": subject,
                    "icon": get_subject_icon(subject),
                    "color": get_subject_color(subject),
                }
        return jsonify({
            "success": True,
            "subjects": list(subjects.values()),
            "total": len(subjects),
        })
    except Exception as e:
        app.logger.error(f"Error getting subjects: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/learn/chapters", methods=["GET"])
@require_auth
def learn_get_chapters():
    try:
        subject = request.args.get("subject")
        if not subject:
            return jsonify({"error": "Subject required"}), 400
        results = vector_db.collection.get(where={"subject": {"$eq": subject}})
        chapters = {}
        for metadata in results.get("metadatas", []):
            chapter = metadata.get("chapter", "Unknown")
            if chapter not in chapters:
                chapters[chapter] = {
                    "name": chapter,
                    "subject": subject,
                    "document_count": 0,
                }
            chapters[chapter]["document_count"] += 1
        chapter_list = sorted(chapters.values(), key=lambda c: c["name"])
        return jsonify({
            "success": True,
            "subject": subject,
            "chapters": chapter_list,
            "total": len(chapter_list),
        })
    except Exception as e:
        app.logger.error(f"Error getting chapters: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/learn/content", methods=["POST"])
@require_auth
def learn_get_content():
    try:
        data = request.get_json() or {}
        subject = data.get("subject")
        chapter = data.get("chapter")
        if not subject or not chapter:
            return jsonify({"error": "Subject and chapter required"}), 400
        force = bool(data.get("force"))

        if not force:
            hit = ai_cache.get(AiCache.KIND_CHAPTER, subject, chapter)
            if hit:
                return jsonify({
                    "success": True,
                    "subject": subject,
                    "chapter": chapter,
                    "summary": hit.get("summary", ""),
                    "eli5": hit.get("eli5", ""),
                    "mnemonics": hit.get("mnemonics", []),
                    "examples": hit.get("examples", []),
                    "key_takeaways": hit.get("key_takeaways", []),
                    "flashcards": hit.get("flashcards", []),
                    "quiz": hit.get("quiz", []),
                    "cached": True,
                    "cached_at": hit.get("_cached_at"),
                })

        context_result = retriever.retrieve_by_chapter(chapter, subject)
        context = context_result.get("context", "")
        if not context or context == "No relevant context found.":
            return jsonify({"error": "No content found for this chapter"}), 404

        pack = gemini.generate_learning_pack(context, chapter)
        if not pack.get("success"):
            return jsonify({"success": False, "error": pack.get("error")}), 500

        quiz_data = gemini.generate_quiz(context, num_questions=5, difficulty="medium")
        quiz = quiz_data.get("quiz", []) if quiz_data.get("success") else []

        stored = ai_cache.put(
            AiCache.KIND_CHAPTER,
            subject,
            {
                "summary": pack.get("summary", ""),
                "eli5": pack.get("eli5", ""),
                "mnemonics": pack.get("mnemonics", []),
                "examples": pack.get("examples", []),
                "key_takeaways": pack.get("key_takeaways", []),
                "flashcards": pack.get("flashcards", []),
                "quiz": quiz,
            },
            chapter=chapter,
        )
        return jsonify({
            "success": True,
            "subject": subject,
            "chapter": chapter,
            "summary": stored.get("summary", ""),
            "eli5": stored.get("eli5", ""),
            "mnemonics": stored.get("mnemonics", []),
            "examples": stored.get("examples", []),
            "key_takeaways": stored.get("key_takeaways", []),
            "flashcards": stored.get("flashcards", []),
            "quiz": stored.get("quiz", []),
            "cached": False,
        })
    except Exception as e:
        app.logger.error(f"Error getting learning content: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/learn/ask", methods=["POST"])
@require_auth
def learn_ask():
    try:
        data = request.get_json() or {}
        subject = data.get("subject")
        chapter = data.get("chapter")
        question = data.get("question", "").strip()
        if not subject or not chapter or not question:
            return jsonify({"error": "Subject, chapter, and question required"}), 400
        force = bool(data.get("force"))
        if not force:
            hit = ai_cache.get(AiCache.KIND_ASK, subject, chapter, question)
            if hit:
                return jsonify({
                    "success": True,
                    "answer": hit.get("answer", ""),
                    "sources": hit.get("sources", 0),
                    "cached": True,
                    "cached_at": hit.get("_cached_at"),
                })
        results = retriever.retrieve_in_chapter(question, chapter, subject)
        context = results.get("context") or retriever.retrieve_by_chapter(chapter, subject).get("context", "")
        answer_result = gemini.answer_question(context, question)
        if not answer_result.get("success"):
            return jsonify({"success": False, "error": answer_result.get("error")}), 500
        stored = ai_cache.put(
            AiCache.KIND_ASK,
            subject,
            {"answer": answer_result.get("answer", ""), "sources": results.get("total_retrieved", 0)},
            chapter=chapter,
            prompt_key=question,
        )
        return jsonify({
            "success": True,
            "answer": stored.get("answer", ""),
            "sources": stored.get("sources", 0),
            "cached": False,
        })
    except Exception as e:
        app.logger.error(f"Learn ask error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/learn/search", methods=["POST"])
@require_auth
def learn_search():
    try:
        data = request.get_json() or {}
        subject = data.get("subject")
        chapter = data.get("chapter")
        query_text = data.get("query", "").strip()
        if not subject or not chapter or not query_text:
            return jsonify({"error": "Subject, chapter, and query required"}), 400
        results = retriever.retrieve_in_chapter(query_text, chapter, subject)
        return jsonify({
            "success": True,
            "query": query_text,
            "total_retrieved": results["total_retrieved"],
            "documents": results["retrieved_documents"],
        })
    except Exception as e:
        app.logger.error(f"Learn search error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
@require_auth
def list_history():
    return jsonify({"success": True, "attempts": users.list_attempts(g.user["id"])})


@app.route("/api/history/<int:attempt_id>", methods=["GET"])
@require_auth
def get_history(attempt_id):
    attempt = users.get_attempt(g.user["id"], attempt_id)
    if not attempt:
        return jsonify({"success": False, "error": "Not found"}), 404
    return jsonify({"success": True, "attempt": attempt})


@app.route("/api/history", methods=["POST"])
@require_auth
def save_history():
    data = request.get_json() or {}
    subject = data.get("subject")
    chapter = data.get("chapter")
    score = data.get("score")
    quiz = data.get("quiz") or []
    answers = data.get("answers") or {}
    if not subject or not chapter or score is None:
        return jsonify({"error": "Subject, chapter, and score required"}), 400
    saved = users.save_attempt(
        user_id=g.user["id"],
        subject=subject,
        chapter=chapter,
        score=int(score),
        num_questions=len(quiz),
        attempt={"quiz": quiz, "answers": answers, "score": int(score)},
    )
    return jsonify({"success": True, "attempt": saved})


def get_subject_icon(subject: str) -> str:
    icons = {
        "English": "📚",
        "Mathematics": "🔢",
        "Marathi": "🌐",
        "General Science": "🔬",
        "Geography": "🗺️",
        "History & Culture": "🏛️",
        "Sanskrit": "🇮🇳",
    }
    return icons.get(subject, "📖")


def get_subject_color(subject: str) -> str:
    colors = {
        "English": "#1976d2",
        "Mathematics": "#388e3c",
        "Marathi": "#d32f2f",
        "General Science": "#7b1fa2",
        "Geography": "#f57c00",
        "History & Culture": "#c2185b",
        "Sanskrit": "#0097a7",
    }
    return colors.get(subject, "#1976d2")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    app.logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    Config.validate_jwt()
    app.run(debug=True, host="0.0.0.0", port=5000)
