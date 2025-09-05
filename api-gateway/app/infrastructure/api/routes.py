from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from datetime import datetime
import httpx
from .models import ServiceCreate, ServiceUpdate, ServiceResponse, HealthResponse
from ...application.use_cases.service_use_cases import ServiceUseCases
from ..persistence.mongodb.service_repository import MongoDBServiceRepository
from ..config import Settings

router = APIRouter(prefix="/api/v1")
settings = Settings()

def get_use_cases() -> ServiceUseCases:
    repository = MongoDBServiceRepository()
    return ServiceUseCases(repository)

@router.get("/healthz", response_model=HealthResponse)
async def health_check(use_cases: ServiceUseCases = Depends(get_use_cases)):
    services = await use_cases.list_services()
    active_services = len([s for s in services if s.is_active])
    return HealthResponse(
        status="ok",
        active_services=active_services,
        total_services=len(services),
        timestamp=datetime.now()
    )

@router.post("/services", response_model=ServiceResponse)
async def register_service(
    service: ServiceCreate,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    existing = await use_cases.get_service_by_name(service.name)
    if existing:
        raise HTTPException(status_code=400, detail="Service already registered")
    
    new_service = await use_cases.register_service(
        Service(
            id=str(uuid4()),
            **service.dict(),
            is_active=True,
            error_count=0,
            average_response_time=0.0
        )
    )
    return new_service

@router.get("/services", response_model=List[ServiceResponse])
async def list_services(
    active_only: bool = False,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    if active_only:
        return await use_cases.list_active_services()
    return await use_cases.list_services()

@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    service = await use_cases.get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service_update: ServiceUpdate,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    existing = await use_cases.get_service(service_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Service not found")
    
    updated = await use_cases.update_service(
        service_id,
        Service(
            **{**existing.__dict__, **service_update.dict(exclude_unset=True)}
        )
    )
    return updated

@router.delete("/services/{service_id}")
async def delete_service(
    service_id: str,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    if not await use_cases.delete_service(service_id):
        raise HTTPException(status_code=404, detail="Service not found")
    return {"status": "ok"}

@router.get("/proxy/{service_name}/{path:path}")
async def proxy_request(
    request: Request,
    service_name: str,
    path: str,
    use_cases: ServiceUseCases = Depends(get_use_cases)
):
    service = await use_cases.get_service_by_name(service_name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if not service.is_active:
        raise HTTPException(status_code=503, detail="Service is not available")
    
    target_url = f"{service.base_url}/{path}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers,
                params=request.query_params,
                content=await request.body(),
                timeout=settings.REQUEST_TIMEOUT
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))