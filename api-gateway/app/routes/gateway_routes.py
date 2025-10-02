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
    "speech": "http://localhost:8004",
    "evaluation": "http://localhost:8005"
}

# Almacenar conexiones WebSocket activas
active_connections: Dict[str, WebSocket] = {}

router = APIRouter()

@router.get("/")
async def root():


@router.get("/health")
async def health_check():

@router.get("/health/services")
