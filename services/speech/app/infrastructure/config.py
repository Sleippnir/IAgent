from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Speech Service"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Audio Configuration
    MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS: List[str] = ["wav", "mp3", "ogg", "webm"]
    DEFAULT_SAMPLE_RATE: int = 16000
    DEFAULT_CHANNELS: int = 1
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "speech_service"
    
    class Config:
        env_file = ".env"