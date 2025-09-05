from abc import abstractmethod
from typing import List, Optional
from ..entities.service import Service
from .base import BaseRepository

class ServiceRepository(BaseRepository[Service]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Service]:
        pass
    
    @abstractmethod
    async def get_active_services(self) -> List[Service]:
        pass
    
    @abstractmethod
    async def get_inactive_services(self) -> List[Service]:
        pass
    
    @abstractmethod
    async def update_health_status(self, id: str, is_active: bool, response_time: float) -> Optional[Service]:
        pass