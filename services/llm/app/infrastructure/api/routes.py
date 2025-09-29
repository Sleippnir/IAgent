from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from ...domain.models import GenerateRequest, GenerateResponse, ModelType
from ...application.use_cases import GenerateTextUseCase, LLMProviderPort
from ..llm_provider import call_openai_gpt5, call_google_gemini, call_openrouter_deepseek


router = APIRouter(prefix="/api/v1")


class RealLLMProvider:
    """Real LLM provider that uses the actual implementations"""
    
    async def generate_text(
        self, 
        prompt: str, 
        model: ModelType, 
        max_tokens: int, 
        temperature: float
    ) -> str:
        """Generate text using real LLM providers"""
        try:
            # The existing functions expect prompt, rubric, transcript
            # For general text generation, we'll use the prompt as the main content
            # and empty strings for rubric and transcript
            if model == ModelType.GPT_4:
                return await call_openai_gpt5(prompt, "", "")
            elif model == ModelType.CLAUDE:
                return await call_google_gemini(prompt, "", "")
            elif model == ModelType.LLAMA:
                return await call_openrouter_deepseek(prompt, "", "")
            else:
                # Default to GPT-4
                return await call_openai_gpt5(prompt, "", "")
        except Exception as e:
            return f"Error generating text: {str(e)}"
    
    def get_model_info(self, model: ModelType) -> dict:
        """Get information about the model"""
        model_info = {
            ModelType.GPT_4: {
                "name": "GPT-5",
                "provider": "OpenAI",
                "max_tokens": 4000,
                "context_window": 128000
            },
            ModelType.CLAUDE: {
                "name": "Gemini 2.5 Pro",
                "provider": "Google",
                "max_tokens": 2048,
                "context_window": 32000
            },
            ModelType.LLAMA: {
                "name": "DeepSeek Chat v3.1",
                "provider": "DeepSeek via OpenRouter",
                "max_tokens": 4000,
                "context_window": 32000
            }
        }
        return model_info.get(model, {"name": "Unknown", "provider": "Unknown", "max_tokens": 0, "context_window": 0})


def get_llm_provider() -> RealLLMProvider:
    """Dependency injection for real LLM provider"""
    return RealLLMProvider()


def get_generate_use_case(
    llm_provider: Annotated[RealLLMProvider, Depends(get_llm_provider)]
) -> GenerateTextUseCase:
    """Dependency injection for text generation use case"""
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
    llm_provider: Annotated[RealLLMProvider, Depends(get_llm_provider)]
):
    """List available models"""
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


# Interview evaluation endpoints
from pydantic import BaseModel
from typing import Optional


class InterviewRequest(BaseModel):
    """Request model for interview evaluation"""
    interview_id: str
    system_prompt: Optional[str] = None
    rubric: Optional[str] = None
    jd: Optional[str] = None
    full_transcript: str


class InterviewResponse(BaseModel):
    """Response model for interview evaluation"""
    interview_id: str
    evaluation_1: Optional[str] = None
    evaluation_2: Optional[str] = None
    evaluation_3: Optional[str] = None
    error: Optional[str] = None


@router.post("/evaluate-interview", response_model=InterviewResponse)
async def evaluate_interview(request: InterviewRequest):
    """Evaluate an interview using multiple LLM providers"""
    try:
        from ...domain.entities.interview import Interview
        
        # Create Interview object
        interview = Interview(
            interview_id=request.interview_id,
            system_prompt=request.system_prompt,
            rubric=request.rubric,
            jd=request.jd,
            full_transcript=request.full_transcript
        )
        
        # Run evaluations using the existing functions
        try:
            interview.evaluation_1 = await call_openai_gpt5(
                interview.system_prompt, interview.rubric, interview.full_transcript
            )
        except Exception as e:
            interview.evaluation_1 = f"OpenAI evaluation failed: {str(e)}"
        
        try:
            interview.evaluation_2 = await call_google_gemini(
                interview.system_prompt, interview.rubric, interview.full_transcript
            )
        except Exception as e:
            interview.evaluation_2 = f"Gemini evaluation failed: {str(e)}"
        
        try:
            interview.evaluation_3 = await call_openrouter_deepseek(
                interview.system_prompt, interview.rubric, interview.full_transcript
            )
        except Exception as e:
            interview.evaluation_3 = f"DeepSeek evaluation failed: {str(e)}"
        
        return InterviewResponse(
            interview_id=interview.interview_id,
            evaluation_1=interview.evaluation_1,
            evaluation_2=interview.evaluation_2,
            evaluation_3=interview.evaluation_3
        )
        
    except Exception as e:
        return InterviewResponse(
            interview_id=request.interview_id,
            error=f"Interview evaluation failed: {str(e)}"
        )


@router.post("/evaluate-interview-file")
async def evaluate_interview_from_file(file_path: str, source_type: str = "file"):
    """Evaluate an interview loaded from file or database"""
    try:
        from ..llm_provider import load_interview_from_source, run_evaluations
        
        # Load interview from source
        interview = load_interview_from_source(source_type, file_path)
        
        # Run evaluations
        evaluated_interview = run_evaluations(interview)
        
        return {
            "interview_id": evaluated_interview.interview_id,
            "evaluation_1": evaluated_interview.evaluation_1,
            "evaluation_2": evaluated_interview.evaluation_2,
            "evaluation_3": evaluated_interview.evaluation_3
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate interview from {source_type}: {str(e)}"
        )