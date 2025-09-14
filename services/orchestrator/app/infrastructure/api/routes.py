from fastapi import APIRouter, Depends
import redis.asyncio as redis

from ...application.use_cases.orchestration_use_cases import OrchestrationUseCases
from ..persistence.redis_session_repository import RedisSessionRepository
from .models import StartSessionRequest, StartSessionResponse, CandidateMessageRequest, CandidateMessageResponse, ImportQuestionsRequest, SessionStatusResponse, ScoringKickoffResponse

router = APIRouter()

# Dependency Injection
def get_redis_client() -> redis.Redis:
    # This should be configured properly, e.g., from environment variables
    return redis.Redis(host="localhost", port=6379, db=0)

def get_session_repository(redis_client: redis.Redis = Depends(get_redis_client)) -> RedisSessionRepository:
    return RedisSessionRepository(redis_client)

def get_orchestration_use_cases(repository: RedisSessionRepository = Depends(get_session_repository)) -> OrchestrationUseCases:
    return OrchestrationUseCases(repository)


@router.get("/healthz")
def health_check():
    return {"status": "ok", "service": "orchestrator"}

@router.post("/roles/import")
async def import_questions(
    req: ImportQuestionsRequest,
    use_cases: OrchestrationUseCases = Depends(get_orchestration_use_cases)
):
    count = await use_cases.import_questions(req.role_id, req.questions)
    return {"ok": True, "count": count}

@router.post("/sessions/start", response_model=StartSessionResponse)
async def start_session(
    req: StartSessionRequest,
    use_cases: OrchestrationUseCases = Depends(get_orchestration_use_cases)
):
    session = await use_cases.start_session(
        role_id=req.role_id,
        jd_digest=req.jd_digest,
        candidate_digest=req.candidate_digest,
        linkedin_digest=req.linkedin_digest,
        extra_notes=req.extra_notes,
        rubric=req.rubric,
    )

    # The first question text needs to be retrieved, but this is not yet implemented
    # in the use case. For now, we return None.
    return StartSessionResponse(session_id=session.session_id, first_question=None)

@router.post("/sessions/candidate_message", response_model=CandidateMessageResponse)
async def candidate_message(
    req: CandidateMessageRequest,
    use_cases: OrchestrationUseCases = Depends(get_orchestration_use_cases)
):
    response_data = await use_cases.candidate_message(req.session_id, req.text)
    return CandidateMessageResponse(**response_data)

@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    use_cases: OrchestrationUseCases = Depends(get_orchestration_use_cases)
):
    status_data = await use_cases.get_session_status(session_id)
    return SessionStatusResponse(**status_data)

@router.post("/sessions/{session_id}/score", response_model=ScoringKickoffResponse)
async def kickoff_scoring(
    session_id: str,
    use_cases: OrchestrationUseCases = Depends(get_orchestration_use_cases)
):
    payload = await use_cases.kickoff_scoring(session_id)
    return ScoringKickoffResponse(session_id=session_id, packaged_payload=payload)
