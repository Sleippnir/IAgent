from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ....domain.entities.service import Service
from ....domain.repositories.service_repository import ServiceRepository
from ...config import Settings

class MongoDBServiceRepository(ServiceRepository):
    def __init__(self):
        settings = Settings()
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["services"]
    
    async def get(self, id: str) -> Optional[Service]:
        doc = await self.collection.find_one({"id": id})
        return Service(**doc) if doc else None
    
    async def list(self) -> List[Service]:
        cursor = self.collection.find({})
        return [Service(**doc) async for doc in cursor]
    
    async def create(self, entity: Service) -> Service:
        await self.collection.insert_one(entity.__dict__)
        return entity
    
    async def update(self, id: str, entity: Service) -> Optional[Service]:
        result = await self.collection.update_one(
            {"id": id},
            {"$set": entity.__dict__}
        )
        return entity if result.modified_count > 0 else None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def get_by_name(self, name: str) -> Optional[Service]:
        doc = await self.collection.find_one({"name": name})
        return Service(**doc) if doc else None
    
    async def get_active_services(self) -> List[Service]:
        cursor = self.collection.find({"is_active": True})
        return [Service(**doc) async for doc in cursor]
    
    async def get_inactive_services(self) -> List[Service]:
        cursor = self.collection.find({"is_active": False})
        return [Service(**doc) async for doc in cursor]
    
    async def update_health_status(self, id: str, is_active: bool, response_time: float) -> Optional[Service]:
        update = {
            "$set": {
                "is_active": is_active,
                "last_health_check": datetime.now(),
                "average_response_time": response_time
            }
        }
        if not is_active:
            update["$inc"] = {"error_count": 1}
        
        result = await self.collection.update_one({"id": id}, update)
        if result.modified_count > 0:
            doc = await self.collection.find_one({"id": id})
            return Service(**doc) if doc else None
        return None