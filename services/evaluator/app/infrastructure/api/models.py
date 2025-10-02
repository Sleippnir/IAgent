"""
Pydantic models for FastAPI request/response serialization.
These models handle API input validation and output serialization.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers for evaluation"""
    OPENAI = "openai"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


class InterviewCreateRequest(BaseModel):
    """Request model for creating a new interview"""
    interview_id: Optional[str] = Field(None, description="Unique identifier for the interview")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt for LLM evaluation")
    rubric: Optional[str] = Field(None, description="Evaluation rubric")
    jd: str = Field(..., description="Job description", min_length=1)
    full_transcript: str = Field(..., description="Complete interview transcript", min_length=1)


class InterviewUpdateRequest(BaseModel):
    """Request model for updating an existing interview"""
    system_prompt: Optional[str] = None
    rubric: Optional[str] = None
    jd: Optional[str] = None
    full_transcript: Optional[str] = None


class EvaluationRequest(BaseModel):
    """Request model for requesting evaluation of an interview"""
    interview_id: str = Field(..., description="ID of the interview to evaluate")
    providers: Optional[List[LLMProvider]] = Field(default=None, description="Specific providers to use for evaluation")


class InterviewResponse(BaseModel):
    """Response model for interview data"""
    interview_id: Optional[str]
    system_prompt: str
    rubric: str
    jd: str
    full_transcript: str
    evaluation_1: Optional[str] = Field(None, description="OpenAI evaluation")
    evaluation_2: Optional[str] = Field(None, description="Google Gemini evaluation")
    evaluation_3: Optional[str] = Field(None, description="DeepSeek evaluation")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EvaluationResponse(BaseModel):
    """Response model for evaluation results"""
    interview_id: str
    provider: LLMProvider
    evaluation: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    service: str
    description: str
    project_name: str
    features: List[str]


class ErrorResponse(BaseModel):
    """Response model for API errors"""
    error: str
    message: str
    details: Optional[dict] = None


class ListInterviewsResponse(BaseModel):
    """Response model for listing interviews"""
    interviews: List[InterviewResponse]
    total: int
    page: int
    per_page: int