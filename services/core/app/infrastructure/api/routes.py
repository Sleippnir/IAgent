from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .models import InterviewCreate, InterviewUpdate, InterviewResponse
from ...application.use_cases.interview_use_cases import InterviewUseCases
from ..persistence.mongodb.interview_repository import MongoDBInterviewRepository

router = APIRouter(prefix="/api/v1")

def get_use_cases() -> InterviewUseCases:
    repository = MongoDBInterviewRepository()
    return InterviewUseCases(repository)

@router.get("/healthz")
def health_check():
    return {"status": "ok", "service": "core"}

@router.post("/interviews", response_model=InterviewResponse)
async def create_interview(interview: InterviewCreate, use_cases: InterviewUseCases = Depends(get_use_cases)):
    return await use_cases.create_interview(interview.candidate_id, interview.position_id)

@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: str, use_cases: InterviewUseCases = Depends(get_use_cases)):
    interview = await use_cases.get_interview(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.get("/interviews", response_model=List[InterviewResponse])
async def list_interviews(use_cases: InterviewUseCases = Depends(get_use_cases)):
    return await use_cases.list_interviews()

@router.patch("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview_status(interview_id: str, update: InterviewUpdate, use_cases: InterviewUseCases = Depends(get_use_cases)):
    interview = await use_cases.update_interview_status(interview_id, update.status)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview