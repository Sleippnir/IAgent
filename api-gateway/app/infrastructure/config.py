from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "API Gateway"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Service Configuration
    REQUEST_TIMEOUT: float = 30.0  # seconds
    MAX_RETRIES: int = 3
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "api_gateway"
    
    # Services
    CORE_SERVICE_URL: str = "http://localhost:8001"
    LLM_SERVICE_URL: str = "http://localhost:8002"
    SPEECH_SERVICE_URL: str = "http://localhost:8003"
    
    class Config:
        env_file = ".env"