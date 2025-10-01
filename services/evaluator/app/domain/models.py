from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ModelType(str, Enum):
    """Tipos de modelos disponibles"""
    GPT_4 = "gpt-4"
    GPT_3_5 = "gpt-3.5-turbo"
    CLAUDE = "claude-3"
    LLAMA = "llama-2"


class Message(BaseModel):
    """Modelo para mensajes individuales"""
    role: str  # system, user, assistant
    content: str
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GenerateRequest(BaseModel):
    """Modelo de dominio para requests de generación de texto"""
    text: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    model: Optional[ModelType] = ModelType.GPT_4
    messages: Optional[List[Message]] = None
    system_prompt: Optional[str] = None


class GenerateResponse(BaseModel):
    """Modelo de dominio para respuestas de generación"""
    generated_text: str
    session_id: str
    timestamp: datetime
    processing_time: float
    model_used: str
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptContext(BaseModel):
    """Contexto para prompts"""
    conversation_history: List[Message] = []
    user_preferences: Optional[Dict[str, Any]] = None
    session_metadata: Optional[Dict[str, Any]] = None


class PromptRequest(BaseModel):
    """Request completo con contexto"""
    prompt: str
    context: Optional[PromptContext] = None
    generation_config: Optional[Dict[str, Any]] = None