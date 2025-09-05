from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "LLM Service"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # LLM Configuration
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS: int = 150
    DEFAULT_TEMPERATURE: float = 0.7
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "llm_service"
    
    class Config:
        env_file = ".env"