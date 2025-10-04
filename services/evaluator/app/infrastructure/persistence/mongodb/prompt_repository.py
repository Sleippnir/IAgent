from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ....domain.entities.prompt import Prompt
from ....domain.repositories.prompt_repository import PromptRepository
from ...config import Settings

class MongoDBPromptRepository(PromptRepository):
    def __init__(self):
        settings = Settings()
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["prompts"]
    
    async def get(self, id: str) -> Optional[Prompt]:
        doc = await self.collection.find_one({"id": id})
        return Prompt(**doc) if doc else None
    
    async def list(self) -> List[Prompt]:
        cursor = self.collection.find({})
        return [Prompt(**doc) async for doc in cursor]
    
    async def create(self, entity: Prompt) -> Prompt:
        await self.collection.insert_one(entity.__dict__)
        return entity
    
    async def update(self, id: str, entity: Prompt) -> Optional[Prompt]:
        result = await self.collection.update_one(
            {"id": id},
            {"$set": entity.__dict__}
        )
        return entity if result.modified_count > 0 else None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def get_by_model(self, model: str) -> List[Prompt]:
        cursor = self.collection.find({"model": model})
        return [Prompt(**doc) async for doc in cursor]
    
    async def get_unprocessed(self) -> List[Prompt]:
        cursor = self.collection.find({"processed_at": None})
        return [Prompt(**doc) async for doc in cursor]
    
    async def get_with_errors(self) -> List[Prompt]:
        cursor = self.collection.find({"error": {"$ne": None}})
        return [Prompt(**doc) async for doc in cursor]