from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Audio:
    id: str
    content: bytes
    sample_rate: int
    channels: int
    format: str
    created_at: datetime
    duration: float
    transcription: Optional[str] = None
    segments: Optional[List[dict]] = None
    error: Optional[str] = None