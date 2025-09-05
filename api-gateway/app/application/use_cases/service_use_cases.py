from datetime import datetime
from typing import List, Optional
import httpx
from ...domain.entities.service import Service
from ...domain.repositories.service_repository import ServiceRepository

class ServiceUseCases:
    def __init__(self, repository: ServiceRepository):
        self.repository = repository
    
    async def register_service(self, service: Service) -> Service:
        return await self.repository.create(service)
    
    async def get_service(self, id: str) -> Optional[Service]:
        return await self.repository.get(id)
    
    async def get_service_by_name(self, name: str) -> Optional[Service]:
        return await self.repository.get_by_name(name)
    
    async def list_services(self) -> List[Service]:
        return await self.repository.list()
    
    async def list_active_services(self) -> List[Service]:
        return await self.repository.get_active_services()
    
    async def update_service(self, id: str, service: Service) -> Optional[Service]:
        return await self.repository.update(id, service)
    
    async def delete_service(self, id: str) -> bool:
        return await self.repository.delete(id)
    
    async def check_service_health(self, service: Service) -> bool:
        try:
            start_time = datetime.now()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{service.base_url}{service.health_endpoint}",
                    timeout=5.0
                )
            response_time = (datetime.now() - start_time).total_seconds()
            
            is_healthy = response.status_code == 200
            await self.repository.update_health_status(
                service.id,
                is_healthy,
                response_time
            )
            return is_healthy
        except Exception:
            await self.repository.update_health_status(
                service.id,
                False,
                0.0
            )
            return False