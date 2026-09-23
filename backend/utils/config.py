import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.1-70b-versatile"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    CHROMA_DB_PATH: str = "./chromadb"
    SQLITE_DB_PATH: str = "./database/autosar_ai.db"
    UPLOAD_FOLDER: str = "./uploads"
    REPORT_FOLDER: str = "./reports"
    MAX_UPLOAD_SIZE_MB: int = 50
    OCR_ENABLED: bool = True
    STREAMING_RESPONSE: bool = True
    TOP_K_RETRIEVAL: int = 5
    TEMPERATURE: float = 0.1

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.REPORT_FOLDER, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
