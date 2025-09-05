from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ....domain.entities.interview import Interview
from ....domain.repositories.interview_repository import InterviewRepository
from ...config import Settings

class MongoDBInterviewRepository(InterviewRepository):
    def __init__(self):
        settings = Settings()
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["interviews"]
    
    async def get(self, id: str) -> Optional[Interview]:
        doc = await self.collection.find_one({"id": id})
        return Interview(**doc) if doc else None
    
    async def list(self) -> List[Interview]:
        cursor = self.collection.find({})
        return [Interview(**doc) async for doc in cursor]
    
    async def create(self, entity: Interview) -> Interview:
        await self.collection.insert_one(entity.__dict__)
        return entity
    
    async def update(self, id: str, entity: Interview) -> Optional[Interview]:
        result = await self.collection.update_one(
            {"id": id},
            {"$set": entity.__dict__}
        )
        return entity if result.modified_count > 0 else None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def get_by_candidate(self, candidate_id: str) -> List[Interview]:
        cursor = self.collection.find({"candidate_id": candidate_id})
        return [Interview(**doc) async for doc in cursor]
    
    async def get_by_position(self, position_id: str) -> List[Interview]:
        cursor = self.collection.find({"position_id": position_id})
        return [Interview(**doc) async for doc in cursor]
    
    async def get_by_status(self, status: str) -> List[Interview]:
        cursor = self.collection.find({"status": status})
        return [Interview(**doc) async for doc in cursor]