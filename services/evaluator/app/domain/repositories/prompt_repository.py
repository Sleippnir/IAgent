from abc import abstractmethod
from typing import Optional, List
from ..entities.prompt import Prompt
from .base import BaseRepository

class PromptRepository(BaseRepository[Prompt]):
    @abstractmethod
    async def get_by_model(self, model: str) -> List[Prompt]:
        pass
    
    @abstractmethod
    async def get_unprocessed(self) -> List[Prompt]:
        pass
    
    @abstractmethod
    async def get_with_errors(self) -> List[Prompt]:
        pass