from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Prompt:
    id: str
    template: str
    parameters: Dict[str, Any]
    created_at: datetime
    model: str
    max_tokens: int
    temperature: float
    response: Optional[str] = None
    processed_at: Optional[datetime] = None
    error: Optional[str] = None