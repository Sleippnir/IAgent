from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Service:
    id: str
    name: str
    base_url: str
    health_endpoint: str
    routes: List[str]
    is_active: bool
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    average_response_time: float = 0.0