from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Dict
import json

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración de servicios backend
SERVICES = {
    "orchestrator": "http://localhost:8001",
    "core": "http://localhost:8002",
    "llm": "http://localhost:8003",
    "speech": "http://speech:8004",
    "evaluation": "http://localhost:8005"
}

# Almacenar conexiones WebSocket activas
active_connections: Dict[str, WebSocket] = {}

router = APIRouter()

@router.get("/")
async def root():
    """
    Endpoint raíz que devuelve información básica del API Gateway
    """
    return {
        "message": "API Gateway funcionando correctamente",
        "version": "1.0.0",
        "servicios_disponibles": list(SERVICES.keys())
    }

@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud del API Gateway
    """
    return {"status": "healthy", "timestamp": "2025-01-09"}

@router.get("/health/services")
async def services_health_check():
    """
    Endpoint para verificar la salud de todos los servicios conectados
    """
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                services_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url,
                    "response_code": response.status_code
                }
        except Exception as e:
            services_status[service_name] = {
                "status": "unreachable",
                "url": service_url,
                "error": str(e)
            }
    
    # Determinar estado general
    all_healthy = all(status["status"] == "healthy" for status in services_status.values())
    
    return {
        "gateway_status": "healthy",
        "overall_status": "healthy" if all_healthy else "degraded",
        "services": services_status,
        "timestamp": "2025-01-09"
    }


@router.api_route("/api/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service_name: str, path: str, request: Request):
    """
    Proxy que redirige las solicitudes a los microservicios correspondientes
    
    Args:
        service_name: Nombre del servicio (orchestrator, core, llm, speech, evaluation)
        path: Ruta específica del endpoint en el microservicio
        request: Objeto de solicitud HTTP
    
    Returns:
        Respuesta del microservicio correspondiente
    """
    
    # Verificar si el servicio existe
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, 
            detail=f"Servicio '{service_name}' no encontrado. Servicios disponibles: {list(SERVICES.keys())}"
        )
    
    # Construir URL del servicio de destino
    target_url = f"{SERVICES[service_name]}/api/v1/{path}"
    
    # Obtener parámetros de consulta
    query_params = str(request.url.query)
    if query_params:
        target_url += f"?{query_params}"
    
    try:
        # Crear cliente HTTP asíncrono
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Obtener el cuerpo de la solicitud si existe
            body = await request.body()
            
            # Realizar la solicitud al microservicio
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=body
            )
            
            # Log de la solicitud
            logger.info(f"Proxy: {request.method} {target_url} -> {response.status_code}")
            
            # Devolver la respuesta del microservicio
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError as e:
        logger.error(f"Error de conexión con {service_name}: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Servicio '{service_name}' no disponible"
        )
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor"
        )