import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    OPENAI_API_KEY = os.getenv("OPENAI_SECRET_TOKEN", '')
    OPENAI_API_BASE = os.getenv("OPENAI_BASE_HOST", '')

    OLLAMA_API_KEY = os.getenv("OLLAMA_SECRET_TOKEN", '')
    OLLAMA_API_BASE = os.getenv("OLLAMA_BASE_HOST", '')
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", '')
    TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID", '')