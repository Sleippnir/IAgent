from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .models import PromptCreate, PromptResponse
from ...application.use_cases.prompt_use_cases import PromptUseCases
from ..persistence.mongodb.prompt_repository import MongoDBPromptRepository
from ..config import Settings

router = APIRouter(prefix="/api/v1")
settings = Settings()

def get_use_cases() -> PromptUseCases:
    repository = MongoDBPromptRepository()
    return PromptUseCases(repository)

@router.get("/healthz")
def health_check():
    return {"status": "ok", "service": "llm"}

@router.post("/prompts", response_model=PromptResponse)
async def create_prompt(
    prompt: PromptCreate,
    use_cases: PromptUseCases = Depends(get_use_cases)
):
    return await use_cases.create_prompt(
        template=prompt.template,
        parameters=prompt.parameters,
        model=prompt.model or settings.DEFAULT_MODEL,
        max_tokens=prompt.max_tokens or settings.DEFAULT_MAX_TOKENS,
        temperature=prompt.temperature or settings.DEFAULT_TEMPERATURE
    )

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: str, use_cases: PromptUseCases = Depends(get_use_cases)):
    prompt = await use_cases.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.get("/prompts", response_model=List[PromptResponse])
async def list_prompts(use_cases: PromptUseCases = Depends(get_use_cases)):
    return await use_cases.list_prompts()