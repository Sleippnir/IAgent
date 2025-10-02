"""
API routes for interview evaluation using LLM providers.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from datetime import datetime

from ...domain.entities.interview import Interview
from ...infrastructure.config import get_settings
from ...infrastructure.persistence.supabase.interview_repository import InterviewRepository
from ...helpers import run_evaluations, load_interview_from_source
from ..api.models import (
    EvaluationRequest,
    EvaluationResponse,
    InterviewResponse,
    LLMProvider,
    ErrorResponse
)
from .routes import interview_to_response

router = APIRouter(prefix="/api/v1", tags=["evaluation"])

# Dependency to get repository
def get_interview_repository():
    return InterviewRepository()


@router.post("/evaluate", response_model=InterviewResponse)
async def evaluate_interview(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """
    Evaluate an interview using LLM providers.
    This endpoint triggers the evaluation process and returns the updated interview.
    """
    try:
        # Get the interview from repository
        interview = await repository.get_by_id(request.interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Run evaluations (this calls all LLM providers)
        evaluated_interview = await run_evaluations(interview)
        
        # Save the updated interview with evaluations
        updated_interview = await repository.update(evaluated_interview)
        
        return interview_to_response(updated_interview)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate interview: {str(e)}")


@router.post("/evaluate/file", response_model=InterviewResponse)
async def evaluate_interview_from_file(
    file_path: str,
    background_tasks: BackgroundTasks,
    save_to_db: bool = True,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """
    Load an interview from a file and evaluate it.
    Optionally save the results to the database.
    """
    try:
        # Load interview from file
        interview = load_interview_from_source('file', file_path)
        
        # Run evaluations
        evaluated_interview = await run_evaluations(interview)
        
        # Save to database if requested
        if save_to_db:
            # Check if interview already exists
            existing = await repository.get_by_id(evaluated_interview.interview_id) if evaluated_interview.interview_id else None
            
            if existing:
                updated_interview = await repository.update(evaluated_interview)
            else:
                updated_interview = await repository.create(evaluated_interview)
        else:
            updated_interview = evaluated_interview
        
        return interview_to_response(updated_interview)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Interview file not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate interview from file: {str(e)}")


@router.get("/evaluate/status/{interview_id}")
async def get_evaluation_status(
    interview_id: str,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """
    Get the evaluation status of an interview.
    Returns which evaluations have been completed.
    """
    try:
        interview = await repository.get_by_id(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return {
            "interview_id": interview_id,
            "evaluations": {
                "openai_gpt5": {
                    "completed": interview.evaluation_1 is not None,
                    "provider": "OpenAI GPT-5",
                    "has_content": bool(interview.evaluation_1)
                },
                "google_gemini": {
                    "completed": interview.evaluation_2 is not None,
                    "provider": "Google Gemini",
                    "has_content": bool(interview.evaluation_2)
                },
                "deepseek": {
                    "completed": interview.evaluation_3 is not None,
                    "provider": "DeepSeek via OpenRouter",
                    "has_content": bool(interview.evaluation_3)
                }
            },
            "total_completed": sum([
                1 for eval in [interview.evaluation_1, interview.evaluation_2, interview.evaluation_3]
                if eval is not None
            ]),
            "all_completed": all([
                interview.evaluation_1 is not None,
                interview.evaluation_2 is not None,
                interview.evaluation_3 is not None
            ])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation status: {str(e)}")


@router.post("/evaluate/batch")
async def evaluate_interviews_batch(
    interview_ids: List[str],
    background_tasks: BackgroundTasks,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """
    Evaluate multiple interviews in batch.
    This is an async operation that runs in the background.
    """
    try:
        settings = get_settings()
        
        # Validate interview IDs exist
        valid_interviews = []
        for interview_id in interview_ids:
            interview = await repository.get_by_id(interview_id)
            if interview:
                valid_interviews.append(interview)
        
        if not valid_interviews:
            raise HTTPException(status_code=404, detail="No valid interviews found")
        
        # Add batch evaluation task to background
        async def batch_evaluation_task():
            """Background task for batch evaluation"""
            for interview in valid_interviews:
                try:
                    evaluated_interview = await run_evaluations(interview)
                    await repository.update(evaluated_interview)
                except Exception as e:
                    print(f"Failed to evaluate interview {interview.interview_id}: {e}")
        
        background_tasks.add_task(batch_evaluation_task)
        
        return {
            "message": f"Batch evaluation started for {len(valid_interviews)} interviews",
            "interview_ids": [i.interview_id for i in valid_interviews],
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch evaluation: {str(e)}")


@router.get("/providers")
async def get_available_providers():
    """Get information about available LLM providers and their status"""
    try:
        settings = get_settings()
        
        providers = {
            "openai": {
                "name": "OpenAI GPT-5",
                "model": settings.OPENAI_MODEL,
                "available": bool(settings.OPENAI_API_KEY),
                "description": "OpenAI's latest GPT model"
            },
            "gemini": {
                "name": "Google Gemini",
                "model": settings.GEMINI_MODEL,
                "available": bool(settings.GOOGLE_API_KEY),
                "description": "Google's Gemini model"
            },
            "deepseek": {
                "name": "DeepSeek via OpenRouter",
                "model": settings.DEEPSEEK_MODEL,
                "available": bool(settings.OPENROUTER_API_KEY),
                "description": "DeepSeek model accessed through OpenRouter"
            }
        }
        
        return {
            "providers": providers,
            "total_available": sum(1 for p in providers.values() if p["available"]),
            "evaluation_enabled": settings.ENABLE_MULTIPLE_EVALUATIONS
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get provider information: {str(e)}")