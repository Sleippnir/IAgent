from typing import Protocol
from datetime import datetime
import time
import asyncio

from ..domain.models import GenerateRequest, GenerateResponse, ModelType


class LLMProviderPort(Protocol):
    """Puerto para proveedores de LLM"""
    
    async def generate_text(
        self, 
        prompt: str, 
        model: ModelType, 
        max_tokens: int, 
        temperature: float
    ) -> str:
        """Genera texto usando el proveedor de LLM"""
        ...
    
    def get_model_info(self, model: ModelType) -> dict:
        """Obtiene información del modelo"""
        ...


class GenerateTextUseCase:
    """Caso de uso para generación de texto"""
    
    def __init__(self, llm_provider: LLMProviderPort):
        self.llm_provider = llm_provider
    
    async def execute(self, request: GenerateRequest) -> GenerateResponse:
        """Ejecuta la generación de texto"""
        start_time = time.time()
        
        try:
            # Preparar el prompt con contexto si existe
            full_prompt = self._prepare_prompt(request)
            
            # Generar texto
            generated_text = await self.llm_provider.generate_text(
                prompt=full_prompt,
                model=request.model or ModelType.GPT_4,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7
            )
            
            processing_time = time.time() - start_time
            
            # Obtener información del modelo
            model_info = self.llm_provider.get_model_info(request.model or ModelType.GPT_4)
            
            return GenerateResponse(
                generated_text=generated_text,
                session_id=request.session_id,
                timestamp=datetime.now(),
                processing_time=processing_time,
                model_used=str(request.model or ModelType.GPT_4),
                tokens_used=len(generated_text.split()),  # Estimación simple
                metadata={
                    "model_info": model_info,
                    "prompt_length": len(full_prompt),
                    "context_provided": bool(request.context),
                    "llm_service_version": "1.0.0"
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return GenerateResponse(
                generated_text="Lo siento, no pude generar una respuesta en este momento.",
                session_id=request.session_id,
                timestamp=datetime.now(),
                processing_time=processing_time,
                model_used=str(request.model or ModelType.GPT_4),
                metadata={
                    "error": str(e),
                    "llm_service_version": "1.0.0"
                }
            )
    
    def _prepare_prompt(self, request: GenerateRequest) -> str:
        """Prepara el prompt con contexto"""
        prompt_parts = []
        
        # Agregar system prompt si existe
        if request.system_prompt:
            prompt_parts.append(f"System: {request.system_prompt}")
        
        # Agregar contexto si existe
        if request.context:
            context_str = str(request.context)
            prompt_parts.append(f"Context: {context_str}")
        
        # Agregar mensajes previos si existen
        if request.messages:
            for message in request.messages:
                prompt_parts.append(f"{message.role}: {message.content}")
        
        # Agregar el texto principal
        prompt_parts.append(f"User: {request.text}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)