from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "LLM Interview Evaluation Service"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # LLM Provider API Keys (from global env)
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # LLM Model Configuration
    OPENAI_MODEL: str = "gpt-5"
    GEMINI_MODEL: str = "gemini-2.5-pro"
    DEEPSEEK_MODEL: str = "deepseek/deepseek-chat-v3.1"
    
    # Default LLM Parameters for Interview Evaluation
    DEFAULT_MAX_TOKENS: int = 2000  # Increased for detailed evaluations
    DEFAULT_TEMPERATURE: float = 0.3  # Lower temperature for more consistent evaluations
    
    # Interview Evaluation Settings
    ENABLE_MULTIPLE_EVALUATIONS: bool = True
    EVALUATION_PROVIDERS: List[str] = ["openai", "gemini", "deepseek"]
    
    # Storage configuration (from global env)
    STORAGE_PATH: str = "./app/storage"
    INTERVIEW_DATA_PATH: str = "./app/storage/interviews"
    SAMPLE_INTERVIEW_FILE: str = "sample_interview.json"
    
    # Supabase Configuration (from global env)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    
    # Development/Debug settings (from global env)
    DEBUG: bool = False
    RELOAD: bool = True
    DEVELOPMENT_MODE: bool = True
    DEBUG_LEVEL: str = "INFO"
    LOG_LEVEL: str = "INFO"
    
    # OpenRouter Configuration
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Conversation limits (from global env)
    MAX_TECHNICAL_QUESTIONS: int = 10
    MAX_GENERAL_QUESTIONS: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from shared .env file


# Singleton instance for easy access throughout the application
_settings = None

def get_settings() -> Settings:
    """Get the settings instance. Creates it if it doesn't exist."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings