import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Codebase Archaeologist"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./codebase_archaeologist.db")
    
    # AI Config
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini") # gemini, openai, claude, mock
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    # GitHub
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN", None)
    
    # File Limits & Storage
    REPO_STORAGE_DIR: str = os.getenv("REPO_STORAGE_DIR", "./storage/repositories")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    MAX_REPO_SIZE_MB: int = int(os.getenv("MAX_REPO_SIZE_MB", "250"))
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
