import os
from dotenv import load_dotenv


class Config:
    def __init__(self) -> None:
        load_dotenv()

        self.OPENAI_API_KEY = os.getenv("OPENAI_SECRET_TOKEN", '')
        self.OPENAI_API_BASE = os.getenv("OPENAI_BASE_HOST", '')

        self.OLLAMA_API_KEY = os.getenv("OLLAMA_SECRET_TOKEN", '')
        self.OLLAMA_API_BASE = os.getenv("OLLAMA_BASE_HOST", '')