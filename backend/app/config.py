"""Application configuration from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "3306"))
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sakoon")
DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# MySQL connector format (raw)
MYSQL_CONFIG = {
    "host": DATABASE_HOST,
    "port": DATABASE_PORT,
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "database": DATABASE_NAME,
}

# OpenRouter API (100+ models: Llama, Gemini, Claude, etc.)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3-8b-instruct",  # OpenRouter model ID
)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# HuggingFace
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_CHAT_MODEL = os.getenv("HF_CHAT_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")

# Admin
ADMIN_KEY = os.getenv("ADMIN_KEY", "sakoon-admin-secret-change-in-prod")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sakoon123")  # Change in production

# App
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Set USE_SQLITE=true in .env only if you want file-based SQLite instead of MySQL
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data" / "sakoon.db"

# ─── Text-to-Speech ───────────────────────────────────────────────────────────
# TTS_PROVIDER: "edge" (default, no local model) | "xtts" (Coqui XTTS-v2, local GPU)
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge")
# Default Edge-TTS neural voice (used when TTS_PROVIDER="edge")
EDGE_TTS_DEFAULT_VOICE = os.getenv("EDGE_TTS_DEFAULT_VOICE", "en-US-AriaNeural")
# Set to "true" to load and use Coqui XTTS-v2 instead of Edge-TTS
USE_XTTS = os.getenv("USE_XTTS", "false").lower() in ("1", "true", "yes")
# Optional path to a short reference WAV for XTTS-v2 voice cloning (empty = default speaker)
XTTS_REFERENCE_WAV = os.getenv("XTTS_REFERENCE_WAV", "")
