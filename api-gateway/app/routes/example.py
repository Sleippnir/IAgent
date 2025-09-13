#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rutas de Ejemplo

Este archivo contiene ejemplos de cómo definir rutas específicas en el API Gateway.
Puede incluir endpoints personalizados, agregación de datos, o lógica específica del gateway.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)

# Crear router para las rutas de ejemplo
router = APIRouter(
    prefix="/api/v1/example",
    tags=["Ejemplos"],
    responses={404: {"description": "No encontrado"}}
)

# Modelos de datos
class HealthStatus(BaseModel):
    """Modelo para el estado de salud de un servicio"""
    service: str
    status: str
    response_time_ms: float
    timestamp: str

class AggregatedResponse(BaseModel):
    """Modelo para respuestas agregadas de múltiples servicios"""
    success: bool
    data: Dict[str, Any]
    services_consulted: List[str]
    total_response_time_ms: float

# Configuración de servicios
SERVICES = {
    "core": "http://localhost:8001",
    "llm": "http://localhost:8002",
    "speech": "http://localhost:8003"
}

@router.get("/health-all", response_model=List[HealthStatus])
async def check_all_services_health():
    """
    Verifica el estado de salud de todos los microservicios
    
    Returns:
        Lista con el estado de cada servicio
    """
    health_results = []
    
    async def check_service_health(service_name: str, service_url: str):
        """Función auxiliar para verificar un servicio específico"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                
            end_time = asyncio.get_event_loop().time()
            response_time = (end_time - start_time) * 1000  # Convertir a ms
            
            return HealthStatus(
                service=service_name,
                status="healthy" if response.status_code == 200 else "unhealthy",
                response_time_ms=round(response_time, 2),
                timestamp="2025-01-09T18:41:00Z"
            )
            
        except Exception as e:
            logger.error(f"Error verificando {service_name}: {e}")
            return HealthStatus(
                service=service_name,
                status="error",
                response_time_ms=0.0,
                timestamp="2025-01-09T18:41:00Z"
            )
    
    # Verificar todos los servicios en paralelo
    tasks = [
        check_service_health(name, url) 
        for name, url in SERVICES.items()
    ]
    
    health_results = await asyncio.gather(*tasks)
    return health_results

@router.get("/aggregate-data", response_model=AggregatedResponse)
async def aggregate_services_data():
    """
    Ejemplo de agregación de datos de múltiples servicios
    
    Returns:
        Datos combinados de varios microservicios
    """
    start_time = asyncio.get_event_loop().time()
    aggregated_data = {}
    services_consulted = []
    
    async def fetch_service_data(service_name: str, service_url: str, endpoint: str):
        """Obtiene datos de un servicio específico"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{service_url}/api/v1/{endpoint}")
                
            if response.status_code == 200:
                return service_name, response.json()
            else:
                logger.warning(f"Servicio {service_name} respondió con código {response.status_code}")
                return service_name, {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error obteniendo datos de {service_name}: {e}")
            return service_name, {"error": str(e)}
    
    # Definir qué datos obtener de cada servicio
    service_endpoints = {
        "core": "status",
        "llm": "models",
        "speech": "capabilities"
    }
    
    # Obtener datos de todos los servicios en paralelo
    tasks = [
        fetch_service_data(name, SERVICES[name], endpoint)
        for name, endpoint in service_endpoints.items()
        if name in SERVICES
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Procesar resultados
    for result in results:
        if isinstance(result, tuple):
            service_name, data = result
            aggregated_data[service_name] = data
            services_consulted.append(service_name)
    
    end_time = asyncio.get_event_loop().time()
    total_time = (end_time - start_time) * 1000
    
    return AggregatedResponse(
        success=len(services_consulted) > 0,
        data=aggregated_data,
        services_consulted=services_consulted,
        total_response_time_ms=round(total_time, 2)
    )

@router.post("/broadcast")
async def broadcast_to_services(request: Request):
    """
    Envía la misma solicitud a múltiples servicios
    
    Args:
        request: Solicitud HTTP que se enviará a todos los servicios
        
    Returns:
        Respuestas de todos los servicios
    """
    # Obtener el cuerpo de la solicitud
    body = await request.body()
    headers = dict(request.headers)
    
    async def send_to_service(service_name: str, service_url: str):
        """Envía la solicitud a un servicio específico"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{service_url}/api/v1/process",
                    content=body,
                    headers=headers
                )
                
            return {
                "service": service_name,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "success": response.status_code < 400
            }
            
        except Exception as e:
            logger.error(f"Error enviando a {service_name}: {e}")
            return {
                "service": service_name,
                "status_code": 500,
                "response": {"error": str(e)},
                "success": False
            }
    
    # Enviar a todos los servicios en paralelo
    tasks = [
        send_to_service(name, url)
        for name, url in SERVICES.items()
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        "message": "Solicitud enviada a todos los servicios",
        "results": results,
        "successful_services": [r["service"] for r in results if r["success"]],
        "failed_services": [r["service"] for r in results if not r["success"]]
    }

@router.get("/service-info/{service_name}")
async def get_service_info(service_name: str):
    """
    Obtiene información detallada de un servicio específico
    
    Args:
        service_name: Nombre del servicio a consultar
        
    Returns:
        Información del servicio
    """
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Servicio '{service_name}' no encontrado. Servicios disponibles: {list(SERVICES.keys())}"
        )
    
    service_url = SERVICES[service_name]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Obtener información básica
            info_response = await client.get(f"{service_url}/")
            health_response = await client.get(f"{service_url}/health")
            
        return {
            "service_name": service_name,
            "service_url": service_url,
            "status": "online" if health_response.status_code == 200 else "offline",
            "info": info_response.json() if info_response.status_code == 200 else None,
            "health": health_response.json() if health_response.status_code == 200 else None
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo información de {service_name}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"No se pudo conectar con el servicio '{service_name}'"
        )