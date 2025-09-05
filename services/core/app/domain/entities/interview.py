from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Interview:
    id: str
    candidate_id: str
    position_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    questions: List[str] = None
    responses: List[str] = None