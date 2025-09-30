#!/usr/bin/env python3
"""
Servicio de Speech - Punto de entrada principal
Este servicio maneja operaciones de texto a voz y voz a texto.
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes.speech_routes import router as speech_router
from app.api.context_management import router as context_router

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    try:
        logger.info("Iniciando Speech Service...")
        logger.info("Speech Service iniciado correctamente")
        yield
    except Exception as e:
        logger.error(f"Error inicializando Speech Service: {e}")
        raise
    finally:
        logger.info("Cerrando Speech Service...")
        logger.info("Speech Service cerrado correctamente")

# Crear la aplicación FastAPI
app = FastAPI(
    title="Speech Service",
    description="Servicio de procesamiento de voz y texto",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas del servicio Speech
app.include_router(speech_router)

# Incluir las rutas de gestión de contexto
app.include_router(context_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )