from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson.binary import Binary
from ....domain.entities.audio import Audio
from ....domain.repositories.audio_repository import AudioRepository
from ...config import Settings

class MongoDBAudioRepository(AudioRepository):
    def __init__(self):
        settings = Settings()
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db["audio"]
    
    def _serialize_audio(self, audio: Audio) -> dict:
        audio_dict = audio.__dict__.copy()
        audio_dict['content'] = Binary(audio.content)
        return audio_dict
    
    def _deserialize_audio(self, doc: dict) -> Audio:
        doc['content'] = bytes(doc['content'])
        return Audio(**doc)
    
    async def get(self, id: str) -> Optional[Audio]:
        doc = await self.collection.find_one({"id": id})
        return self._deserialize_audio(doc) if doc else None
    
    async def list(self) -> List[Audio]:
        cursor = self.collection.find({})
        return [self._deserialize_audio(doc) async for doc in cursor]
    
    async def create(self, entity: Audio) -> Audio:
        await self.collection.insert_one(self._serialize_audio(entity))
        return entity
    
    async def update(self, id: str, entity: Audio) -> Optional[Audio]:
        result = await self.collection.update_one(
            {"id": id},
            {"$set": self._serialize_audio(entity)}
        )
        return entity if result.modified_count > 0 else None
    
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def get_by_format(self, format: str) -> List[Audio]:
        cursor = self.collection.find({"format": format})
        return [self._deserialize_audio(doc) async for doc in cursor]
    
    async def get_untranscribed(self) -> List[Audio]:
        cursor = self.collection.find({"transcription": None})
        return [self._deserialize_audio(doc) async for doc in cursor]
    
    async def get_with_errors(self) -> List[Audio]:
        cursor = self.collection.find({"error": {"$ne": None}})
        return [self._deserialize_audio(doc) async for doc in cursor]
    
    async def get_by_duration_range(self, min_duration: float, max_duration: float) -> List[Audio]:
        cursor = self.collection.find({
            "duration": {"$gte": min_duration, "$lte": max_duration}
        })
        return [self._deserialize_audio(doc) async for doc in cursor]