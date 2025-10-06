from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """
    Config del servicio (capa LLM/Evaluator) basada en pydantic BaseSettings.
    - Lee variables desde .env (ver Config.env_file)
    - Los defaults permiten desarrollo local
    """
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"                                      # --> Prefijo de endpoints (si expone API)
    PROJECT_NAME: str = "LLM Interview Evaluation Service"              # --> Nombre del servicio
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]  # --> Orígenes permitidos para front
    
    # LLM Provider API Keys (from global env)
    OPENAI_API_KEY: Optional[str] = None                                 # --> Key OpenAI
    GOOGLE_API_KEY: Optional[str] = None                                  # --> Key Google Gemini
    OPENROUTER_API_KEY: Optional[str] = None                              # --> Key OpenRouter (DeepSeek, etc.)
    DEEPSEEK_API_KEY: Optional[str] = None                                # --> (si fuese directa)
    PERPLEXITY_API_KEY: Optional[str] = None                              # --> (si se usa Perplexity)
    
    # LLM Model Configuration
    OPENAI_MODEL: str = "gpt-5"                                          # --> Modelo target en OpenAI
    GEMINI_MODEL: str = "gemini-2.5-pro"                                 # --> Modelo target en Gemini
    DEEPSEEK_MODEL: str = "deepseek/deepseek-chat-v3.1"                  # --> Modelo target en OpenRouter
    
    # Default LLM Parameters for Interview Evaluation
    DEFAULT_MAX_TOKENS: int = 2000  # Increased for detailed evaluations                      # --> Límite tokens salida (detallado)
    DEFAULT_TEMPERATURE: float = 0.3  # Lower temperature for more consistent evaluations     # --> Baja temperatura = más determinismo
    
    # Interview Evaluation Settings
    ENABLE_MULTIPLE_EVALUATIONS: bool = True                             # --> Ejecutar varios proveedores a la vez
    EVALUATION_PROVIDERS: List[str] = ["openai", "gemini", "deepseek"]   # --> Orden/selección de proveedores
    
    # Storage configuration (from global env)
    STORAGE_PATH: str = "./app/storage"                                  # --> Carpeta base de storage local
    INTERVIEW_DATA_PATH: str = "./app/storage/interviews"                # --> Carpeta de entrevistas (JSON)
    SAMPLE_INTERVIEW_FILE: str = "sample_interview.json"                 # --> Archivo demo
    
    # Supabase Configuration (from global env)
    SUPABASE_URL: Optional[str] = None                                    # --> URL del proyecto
    SUPABASE_ANON_KEY: Optional[str] = None                               # --> Anon (front/dev). Para backend usar SERVICE_ROLE
    
    # Development/Debug settings (from global env)
    DEBUG: bool = False                                                   # --> Flag debug general
    RELOAD: bool = True                                                   # --> Hot reload (si usa server web)
    DEVELOPMENT_MODE: bool = True                                         # --> Modo desarrollo
    DEBUG_LEVEL: str = "INFO"                                             # --> Nivel de debug propio
    LOG_LEVEL: str = "INFO"                                               # --> Nivel de logging general
    
    # OpenRouter Configuration
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"             # --> Endpoint OpenRouter
    
    # Conversation limits (from global env)
    MAX_TECHNICAL_QUESTIONS: int = 10                                     # --> (si entrevista genera preguntas)
    MAX_GENERAL_QUESTIONS: int = 5
    
    class Config:
        env_file = ".env"                                                # --> Lee .env de la raíz
        case_sensitive = True                                            # --> Variables case-sensitive
        extra = "ignore"  # Ignore extra fields from shared .env file    # --> Ignora claves extra del .env compartido



# Singleton instance for easy access throughout the application
# Singleton sencillo (opcional): algunos prefieren get_settings() por lazy-load
_settings = None

def get_settings() -> Settings:
    """
    Get the settings instance. Creates it if it doesn't exist.
    Obtiene/crea instancia única de Settings (útil si querés inyectar).
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
