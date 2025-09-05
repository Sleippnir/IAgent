from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def list(self) -> List[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass