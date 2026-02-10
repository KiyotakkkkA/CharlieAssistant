import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # ---------------- ASSISTANT SETTINGS ------------------
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Чарли")
    ASSISTANT_TIMEZONE = os.getenv("ASSISTANT_TIMEZONE", "Europe/Moscow")

    # --------------- INTEGRATION SETTINGS -----------------
    OPENAI_API_KEY = os.getenv("OPENAI_SECRET_TOKEN", '')
    OPENAI_API_BASE = os.getenv("OPENAI_BASE_HOST", 'https://openrouter.ai/api/v1')

    OLLAMA_API_KEY = os.getenv("OLLAMA_SECRET_TOKEN", '')
    OLLAMA_API_BASE = os.getenv("OLLAMA_BASE_HOST", 'https://ollama.com')
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", '')
    TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", '')

    # ------------------ CACHE SETTINGS --------------------
    CACHE_TTL_SCHEDULE = os.getenv("CACHE_TTL_SCHEDULE", '6h')