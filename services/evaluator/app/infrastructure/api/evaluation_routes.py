"""
Evaluation endpoints - migrated from evaluation-reporting service
These endpoints handle interview evaluation results and statistics
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Union, Literal
from datetime import datetime

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])

# Structured evaluation models based on rubric schema
class CriterionScore(BaseModel):
    score: Literal["very_weak", "weak", "strong", "very_strong"]
    rationale: str
    evidence: List[str]

class TechnicalEvaluation(BaseModel):
    problem_understanding: CriterionScore
    technical_skills: CriterionScore
    rationale: CriterionScore
    communication: CriterionScore

class BehavioralEvaluation(BaseModel):
    question_understanding: CriterionScore
    experience_competence: CriterionScore
    self_awareness: CriterionScore
    communication: CriterionScore

class OverallAssessment(BaseModel):
    quantitative_score: float  # 0-100
    score_calculation: str
    recommendation: Literal["strong_hire", "hire", "no_hire", "strong_no_hire"]
    key_strengths: List[str]
    areas_for_improvement: List[str]
    summary: str

class EvaluationMetadata(BaseModel):
    evaluator: str
    evaluation_timestamp: datetime
    rubric_version: str

class StructuredEvaluationResponse(BaseModel):
    """Structured evaluation response following the rubric schema"""
    interview_type: Literal["technical", "behavioral"]
    technical_evaluation: Optional[TechnicalEvaluation] = None
    behavioral_evaluation: Optional[BehavioralEvaluation] = None
    overall_assessment: OverallAssessment
    metadata: EvaluationMetadata

# Experimental models for mixed interviews (testing only)
class CriterionScoreExtended(BaseModel):
    score: Literal["very_weak", "weak", "strong", "very_strong", "not_applicable"]
    rationale: str
    evidence: List[str]

class MixedEvaluationResponse(BaseModel):
    """EXPERIMENTAL: Mixed interview evaluation response"""
    interview_type: Literal["technical", "behavioral", "mixed"]
    technical_evaluation: Optional[dict] = None  # Flexible for testing
    behavioral_evaluation: Optional[dict] = None  # Flexible for testing
    overall_assessment: dict  # Flexible for testing
    metadata: dict  # Flexible for testing

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

# Structured Evaluation Endpoint - Returns rubric-based evaluation
@router.get("/structured/{interview_id}", response_model=StructuredEvaluationResponse)
async def get_structured_evaluation(interview_id: str):
    """Get structured rubric-based evaluation for a specific interview"""
    from ...infrastructure.llm_provider import load_interview_from_source, get_structured_evaluation
    
    try:
        # Load interview from file (this is what actually exists)
        interview = load_interview_from_source("file", f"{interview_id}.json")
        
        # Get structured evaluation using the rubric schema
        structured_evaluation = await get_structured_evaluation(interview)
        
        return structured_evaluation
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Could not generate structured evaluation for interview {interview_id}: {str(e)}"
        )

# EXPERIMENTAL: Mixed Interview Evaluation Endpoint (for testing custom prompts/schemas)
@router.post("/experimental/mixed/{interview_id}", response_model=MixedEvaluationResponse)
async def get_mixed_evaluation_experimental(
    interview_id: str,
    custom_prompt: Optional[str] = None,
    custom_schema: Optional[dict] = None
):
    """
    EXPERIMENTAL: Get mixed interview evaluation with custom prompts/schemas
    This endpoint allows testing different prompt strategies without affecting main logic
    """
    from ...infrastructure.llm_provider import load_interview_from_source, get_mixed_evaluation_experimental
    
    try:
        # Load interview from file
        interview = load_interview_from_source("file", f"{interview_id}.json")
        
        # Use experimental function with custom parameters
        experimental_evaluation = await get_mixed_evaluation_experimental(
            interview, 
            custom_prompt=custom_prompt,
            custom_schema=custom_schema
        )
        
        return experimental_evaluation
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Experimental evaluation failed for interview {interview_id}: {str(e)}"
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