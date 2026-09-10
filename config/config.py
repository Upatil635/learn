import os
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENV_PATH = os.path.join(_BASE_DIR, ".env")
load_dotenv(_ENV_PATH, override=True)


def _clean_env(value: str) -> str:
    return (value or "").strip().strip('"').strip("'")


class Config:
    DATA_DIR = os.path.join(_BASE_DIR, "data")
    MD_FILES_PATH = os.path.join(_BASE_DIR, "PDFs", "8th")
    CHROMA_DB_PATH = os.path.join(DATA_DIR, "chroma_db")
    APP_DB_PATH = os.path.join(DATA_DIR, "app.db")

    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "learnEasy_embeddings")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "default")

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.6))
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 8000))
    TOP_K_RESULTS = 5

    @staticmethod
    def _reload_env():
        load_dotenv(_ENV_PATH, override=True)

    @staticmethod
    def jwt_secret() -> str:
        Config._reload_env()
        return _clean_env(os.getenv("JWT_SECRET", ""))

    @staticmethod
    def llm_provider() -> str:
        Config._reload_env()
        return _clean_env(os.getenv("LLM_PROVIDER", "lmstudio")).lower() or "lmstudio"

    @staticmethod
    def llm_base_url() -> str:
        Config._reload_env()
        return _clean_env(os.getenv("LLM_BASE_URL", "")) or "http://127.0.0.1:1234/v1"

    @staticmethod
    def llm_api_key() -> str:
        Config._reload_env()
        return _clean_env(os.getenv("LLM_API_KEY", "")) or "lm-studio"

    @staticmethod
    def llm_model() -> str:
        Config._reload_env()
        explicit = _clean_env(os.getenv("LLM_MODEL", ""))
        if explicit:
            return explicit
        if Config.llm_provider() == "gemini":
            return _clean_env(os.getenv("GEMINI_MODEL", "")) or "gemini-3.6-flash"
        return "nvidia/nemotron-3-nano-4b"

    @staticmethod
    def llm_timeout_seconds() -> int:
        Config._reload_env()
        try:
            return int(_clean_env(os.getenv("LLM_TIMEOUT_SECONDS", "")) or "120")
        except ValueError:
            return 120

    @staticmethod
    def gemini_api_key() -> str:
        Config._reload_env()
        return _clean_env(os.getenv("GEMINI_API_KEY", ""))

    @staticmethod
    def gemini_model() -> str:
        Config._reload_env()
        if Config.llm_provider() == "gemini":
            return Config.llm_model()
        return _clean_env(os.getenv("GEMINI_MODEL", "")) or "gemini-3.6-flash"

    @staticmethod
    def validate():
        Config.validate_llm()
        return True

    @staticmethod
    def validate_llm():
        provider = Config.llm_provider()
        if provider in ("lmstudio", "openai", "openai-compatible"):
            if not Config.llm_base_url():
                raise ValueError("LLM_BASE_URL not set in .env file")
            if not Config.llm_model():
                raise ValueError("LLM_MODEL not set in .env file")
        elif provider == "gemini":
            if not Config.gemini_api_key():
                raise ValueError("GEMINI_API_KEY not set in .env file")
        else:
            raise ValueError(
                f"Unknown LLM_PROVIDER '{provider}'. Use lmstudio, openai, or gemini."
            )
        return True

    @staticmethod
    def validate_gemini():
        return Config.validate_llm()

    @staticmethod
    def validate_jwt():
        secret = Config.jwt_secret()
        if not secret or len(secret) < 16:
            raise ValueError("JWT_SECRET not set in .env file (use a long random string)")
        return True
