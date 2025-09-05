from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class AudioMetadata(BaseModel):
    sample_rate: int
    channels: int
    format: str
    duration: float

class AudioCreate(AudioMetadata):
    content: bytes

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: float

class AudioResponse(AudioMetadata):
    id: str
    created_at: datetime
    transcription: Optional[str] = None
    segments: Optional[List[TranscriptionSegment]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True