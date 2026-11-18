"""Paths and settings. Everything that may change between environments comes from env vars."""
import os
import pathlib

try:  # use the OS trust store when available (needed behind some corporate/ISP proxies); not required in Docker
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
INDEX_DIR = pathlib.Path(os.getenv("INDEX_DIR", ROOT / "data" / "index"))
MODEL_DIR = pathlib.Path(os.getenv("MODEL_DIR", ROOT / "models"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
# Free models, tried in order (OpenRouter falls back to the next one if a model is down or rate limited).
# Kept in an env var so a model leaving the free tier is a restart, not a rebuild.
LLM_MODELS = [m.strip() for m in os.getenv(
    "LLM_MODELS",
    "google/gemma-4-31b-it:free,nvidia/nemotron-3-ultra-550b-a55b:free,google/gemma-4-26b-a4b-it:free",
).split(",") if m.strip()]
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1200"))

APP_TITLE = "DarGlobal & Wasalt Property Assistant"
PORT = int(os.getenv("PORT", "7860"))
