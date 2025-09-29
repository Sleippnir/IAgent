"""
Evaluation endpoints - migrated from evaluation-reporting service
These endpoints handle interview evaluation results and statistics
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])

# Real response models based on actual Interview entity structure
class InterviewEvaluationResponse(BaseModel):
    """Response model for interview evaluation results - based on actual Interview entity"""
    interview_id: Optional[str]
    system_prompt: str
    rubric: str
    jd: str
    full_transcript: str
    evaluation_1: Optional[str] = None  # OpenAI evaluation text
    evaluation_2: Optional[str] = None  # Gemini evaluation text  
    evaluation_3: Optional[str] = None  # DeepSeek evaluation text

class ExportRequest(BaseModel):
    interview_id: str
    format: str = "pdf"
    language: str = "es"

# Evaluation Results Endpoints
@router.get("/results/interview/{interview_id}", response_model=InterviewEvaluationResponse)
async def get_interview_results(interview_id: str):
    """Get evaluation results for a specific interview"""
    from ...infrastructure.llm_provider import load_interview_from_source
    
    try:
        # Load interview from file (this is what actually exists)
        # In a real system, this would load from database
        interview = load_interview_from_source("file", f"{interview_id}.json")
        
        return InterviewEvaluationResponse(
            interview_id=interview.interview_id,
            system_prompt=interview.system_prompt,
            rubric=interview.rubric,
            jd=interview.jd,
            full_transcript=interview.full_transcript,
            evaluation_1=interview.evaluation_1,
            evaluation_2=interview.evaluation_2,
            evaluation_3=interview.evaluation_3
        )
    except Exception as e:
        # If file doesn't exist, return a default interview structure
        # This shows what the system actually works with
        from ...domain.entities.interview import Interview
        default_interview = Interview(interview_id=interview_id)
        
        return InterviewEvaluationResponse(
            interview_id=default_interview.interview_id,
            system_prompt=default_interview.system_prompt,
            rubric=default_interview.rubric,
            jd=default_interview.jd,
            full_transcript=default_interview.full_transcript,
            evaluation_1=default_interview.evaluation_1,
            evaluation_2=default_interview.evaluation_2,
            evaluation_3=default_interview.evaluation_3
        )

# Export Endpoint - Only supports JSON export since that's what actually exists
@router.post("/export/{interview_id}")
async def export_interview(
    interview_id: str,
    request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """Export interview evaluation in supported formats"""
    if request.format == "json":
        # Return the actual interview data as JSON
        interview_data = await get_interview_results(interview_id)
        return interview_data
    else:
        raise HTTPException(
            status_code=501, 
            detail=f"Export format '{request.format}' not implemented. Only 'json' is currently supported."
        )