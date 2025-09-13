#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Gateway Principal

Este archivo contiene la configuración principal del API Gateway.
Actúa como punto de entrada único para todas las solicitudes de la aplicación.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.gateway_routes import router as gateway_router
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="API Gateway",
    description="Gateway centralizado para enrutar solicitudes a microservicios",
    version="1.0.0"
)

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas del gateway
app.include_router(gateway_router)

if __name__ == "__main__":
    # Ejecutar el servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )