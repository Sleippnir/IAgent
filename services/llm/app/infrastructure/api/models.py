from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class PromptBase(BaseModel):
    template: str
    parameters: Dict[str, Any]
    model: str
    max_tokens: int
    temperature: float

class PromptCreate(PromptBase):
    pass

class PromptResponse(PromptBase):
    id: str
    created_at: datetime
    response: Optional[str] = None
    processed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True