from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class InterviewBase(BaseModel):
    candidate_id: str
    position_id: str

class InterviewCreate(InterviewBase):
    pass

class InterviewUpdate(BaseModel):
    status: str

class InterviewResponse(InterviewBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: Optional[List[str]] = None
    responses: Optional[List[str]] = None

    class Config:
        from_attributes = True