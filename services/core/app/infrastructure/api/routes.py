# routes.py — Router agregador del CORE
from fastapi import APIRouter, HTTPException, Depends
from typing import List

# Importa desde services/app/infrastructure/api/routers/ --> Con esto el Core expone /api/v1/..
from .routers.candidates import router as candidates_router
from .routers.jobs import router as jobs_router
from .routers.users import router as users_router
from .routers.roles import router as roles_router
from .routers.prompts import router as prompts_router
from .routers.techqa import router as techqa_router
from .routers.techqa_jobs import router as techqa_jobs_router
from .routers.generalqas import router as generalqa_router

# Router agregador del CORE.
router = APIRouter(prefix="/api/v1")

# Colgamos los sub-routers del agregador (NO del app).
router.include_router(candidates_router)
router.include_router(jobs_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(prompts_router)
router.include_router(techqa_router)
router.include_router(techqa_jobs_router)
router.include_router(generalqa_router)

# -----------------------
# Rutas propias del Core
# -----------------------
# Entidades de entrevistas (capa de casos de uso)
from .models import InterviewCreate, InterviewUpdate, InterviewResponse
from ...application.use_cases.interview_use_cases import InterviewUseCases
from ..persistence.postgres.postgres_interview_repository import PostgresInterviewRepository


def get_use_cases() -> InterviewUseCases:
    """
    Inyecta casos de uso con el repo Postgres real (Supabase).
    """
    repository = PostgresInterviewRepository()
    return InterviewUseCases(repository)


@router.get("/healthz")
def health_check():
    """
    Health del Core expuesto bajo /api/v1/healthz
    El API-Gateway proxyea /api/v1/core/healthz → Core /api/v1/healthz.
    """
    return {"status": "ok", "service": "core"}

@router.post("/interviews", response_model=InterviewResponse)
async def create_interview(interview: InterviewCreate, use_cases: InterviewUseCases = Depends(get_use_cases)):
    """
    Crea entrevista vía casos de uso (repo: Postgres/Supabase).
    """
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