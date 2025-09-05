from abc import abstractmethod
from typing import Optional, List
from ..entities.interview import Interview
from .base import BaseRepository

class InterviewRepository(BaseRepository[Interview]):
    @abstractmethod
    async def get_by_candidate(self, candidate_id: str) -> List[Interview]:
        pass
    
    @abstractmethod
    async def get_by_position(self, position_id: str) -> List[Interview]:
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str) -> List[Interview]:
        pass