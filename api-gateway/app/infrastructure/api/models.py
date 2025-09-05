from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    base_url: HttpUrl
    health_endpoint: str
    routes: List[str]

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    is_active: Optional[bool] = None

class ServiceResponse(ServiceBase):
    id: str
    is_active: bool
    last_health_check: Optional[datetime] = None
    error_count: int
    average_response_time: float

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    active_services: int
    total_services: int
    timestamp: datetime