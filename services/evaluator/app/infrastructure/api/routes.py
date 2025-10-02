"""
Main API routes for the LLM Interview Evaluation Service.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from ...domain.entities.interview import Interview
from ...infrastructure.config import get_settings
from ...infrastructure.persistence.supabase.interview_repository import InterviewRepository
from ..api.models import (
    InterviewCreateRequest,
    InterviewUpdateRequest,
    InterviewResponse,
    ListInterviewsResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1", tags=["interviews"])

# Dependency to get repository
def get_interview_repository():
    return InterviewRepository()

# Helper function to convert domain entity to API response
def interview_to_response(interview: Interview) -> InterviewResponse:
    """Convert Interview domain entity to API response model"""
    return InterviewResponse(
        interview_id=interview.interview_id,
        system_prompt=interview.system_prompt,
        rubric=interview.rubric,
        jd=interview.jd,
        full_transcript=interview.full_transcript,
        evaluation_1=interview.evaluation_1,
        evaluation_2=interview.evaluation_2,
        evaluation_3=interview.evaluation_3,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

# Helper function to convert API request to domain entity
def request_to_interview(request: InterviewCreateRequest) -> Interview:
    """Convert API request to Interview domain entity"""
    return Interview(
        interview_id=request.interview_id,
        system_prompt=request.system_prompt,
        rubric=request.rubric,
        jd=request.jd,
        full_transcript=request.full_transcript
    )


@router.post("/interviews", response_model=InterviewResponse, status_code=201)
async def create_interview(
    request: InterviewCreateRequest,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Create a new interview record"""
    try:
        # Convert request to domain entity
        interview = request_to_interview(request)
        
        # Save to repository
        created_interview = await repository.create(interview)
        
        # Convert back to response model
        return interview_to_response(created_interview)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create interview: {str(e)}")


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get a specific interview by ID"""
    try:
        interview = await repository.get_by_id(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
            
        return interview_to_response(interview)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve interview: {str(e)}")


@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    request: InterviewUpdateRequest,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Update an existing interview"""
    try:
        # First, get the existing interview
        existing_interview = await repository.get_by_id(interview_id)
        
        if not existing_interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Update only provided fields
        if request.system_prompt is not None:
            existing_interview.system_prompt = request.system_prompt
        if request.rubric is not None:
            existing_interview.rubric = request.rubric
        if request.jd is not None:
            existing_interview.jd = request.jd
        if request.full_transcript is not None:
            existing_interview.full_transcript = request.full_transcript
            
        # Save updated interview
        updated_interview = await repository.update(existing_interview)
        
        return interview_to_response(updated_interview)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update interview: {str(e)}")


@router.delete("/interviews/{interview_id}", status_code=204)
async def delete_interview(
    interview_id: str,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Delete an interview"""
    try:
        success = await repository.delete(interview_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Interview not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete interview: {str(e)}")


@router.get("/interviews", response_model=ListInterviewsResponse)
async def list_interviews(
    page: int = 1,
    per_page: int = 10,
    has_evaluations: Optional[bool] = None,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """List interviews with optional filtering"""
    try:
        if per_page > 100:
            per_page = 100
        if per_page < 1:
            per_page = 1
        if page < 1:
            page = 1
            
        offset = (page - 1) * per_page
        
        if has_evaluations is not None:
            interviews = await repository.get_by_status(has_evaluations=has_evaluations)
            # Apply pagination manually for filtered results
            total = len(interviews)
            interviews = interviews[offset:offset + per_page]
        else:
            interviews = await repository.list_all(limit=per_page, offset=offset)
            # For simplicity, we'll use the returned count as total
            # In a real implementation, you'd want a separate count query
            total = len(interviews) + offset
        
        interview_responses = [interview_to_response(interview) for interview in interviews]
        
        return ListInterviewsResponse(
            interviews=interview_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list interviews: {str(e)}")


# Mock LLM Provider for testing (referenced in tests)
class RealLLMProvider:
    """Mock LLM provider for testing purposes"""
    
    async def generate_text(self, prompt: str, model: str, max_tokens: int, temperature: float) -> str:
        """Generate text using specified model"""
        # This is a mock implementation for testing
        return f"Generated response for model {model} with prompt: {prompt[:50]}..."