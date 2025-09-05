from datetime import datetime
from typing import List, Optional
from ...domain.entities.interview import Interview
from ...domain.repositories.interview_repository import InterviewRepository

class InterviewUseCases:
    def __init__(self, repository: InterviewRepository):
        self.repository = repository
    
    async def create_interview(self, candidate_id: str, position_id: str) -> Interview:
        interview = Interview(
            id=str(datetime.now().timestamp()),
            candidate_id=candidate_id,
            position_id=position_id,
            status="scheduled",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return await self.repository.create(interview)
    
    async def get_interview(self, interview_id: str) -> Optional[Interview]:
        return await self.repository.get(interview_id)
    
    async def list_interviews(self) -> List[Interview]:
        return await self.repository.list()
    
    async def update_interview_status(self, interview_id: str, status: str) -> Optional[Interview]:
        interview = await self.repository.get(interview_id)
        if interview:
            interview.status = status
            interview.updated_at = datetime.now()
            if status == "completed":
                interview.completed_at = datetime.now()
            return await self.repository.update(interview_id, interview)
        return None