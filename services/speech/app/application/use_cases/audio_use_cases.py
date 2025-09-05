from datetime import datetime
from typing import List, Optional, Dict
from ...domain.entities.audio import Audio
from ...domain.repositories.audio_repository import AudioRepository

class AudioUseCases:
    def __init__(self, repository: AudioRepository):
        self.repository = repository
    
    async def create_audio(self, content: bytes, sample_rate: int, channels: int, format: str, duration: float) -> Audio:
        audio = Audio(
            id=str(datetime.now().timestamp()),
            content=content,
            sample_rate=sample_rate,
            channels=channels,
            format=format,
            created_at=datetime.now(),
            duration=duration
        )
        return await self.repository.create(audio)
    
    async def get_audio(self, audio_id: str) -> Optional[Audio]:
        return await self.repository.get(audio_id)
    
    async def list_audio(self) -> List[Audio]:
        return await self.repository.list()
    
    async def update_transcription(self, audio_id: str, transcription: str, segments: List[Dict] = None) -> Optional[Audio]:
        audio = await self.repository.get(audio_id)
        if audio:
            audio.transcription = transcription
            audio.segments = segments
            return await self.repository.update(audio_id, audio)
        return None
    
    async def update_error(self, audio_id: str, error: str) -> Optional[Audio]:
        audio = await self.repository.get(audio_id)
        if audio:
            audio.error = error
            return await self.repository.update(audio_id, audio)
        return None