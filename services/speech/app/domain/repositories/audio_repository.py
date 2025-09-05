from abc import abstractmethod
from typing import Optional, List
from ..entities.audio import Audio
from .base import BaseRepository

class AudioRepository(BaseRepository[Audio]):
    @abstractmethod
    async def get_by_format(self, format: str) -> List[Audio]:
        pass
    
    @abstractmethod
    async def get_untranscribed(self) -> List[Audio]:
        pass
    
    @abstractmethod
    async def get_with_errors(self) -> List[Audio]:
        pass
    
    @abstractmethod
    async def get_by_duration_range(self, min_duration: float, max_duration: float) -> List[Audio]:
        pass