from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ...domain.models import GenerateRequest, GenerateResponse
from ...application.use_cases import GenerateTextUseCase
from ..llm_provider import MockLLMProvider


router = APIRouter(prefix="/api/v1")


def get_llm_provider() -> MockLLMProvider:
    """Dependency injection para proveedor LLM"""
    return MockLLMProvider()


def get_generate_use_case(
    llm_provider: Annotated[MockLLMProvider, Depends(get_llm_provider)]
) -> GenerateTextUseCase:
    """Dependency injection para caso de uso de generación"""
    return GenerateTextUseCase(llm_provider)


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(
    request: GenerateRequest,
    use_case: Annotated[GenerateTextUseCase, Depends(get_generate_use_case)]
):
    """Endpoint para generar texto usando LLM"""
    try:
        return await use_case.execute(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal LLM service error: {str(e)}"
        )


@router.get("/models")
async def list_models(
    llm_provider: Annotated[MockLLMProvider, Depends(get_llm_provider)]
):
    """Lista los modelos disponibles"""
    from ...domain.models import ModelType
    
    models = []
    for model_type in ModelType:
        model_info = llm_provider.get_model_info(model_type)
        models.append({
            "id": model_type.value,
            "name": model_info.get("name", model_type.value),
            "provider": model_info.get("provider", "Unknown"),
            "max_tokens": model_info.get("max_tokens", 0),
            "context_window": model_info.get("context_window", 0)
        })
    
    return {"models": models}