#!/usr/bin/env python3
"""
Paquete de rutas del Speech Service

Este paquete contiene todas las rutas HTTP del servicio de speech.
"""

from .speech_routes import router as speech_router

__all__ = [
    "speech_router"
]

__version__ = "1.0.0"
__description__ = "Speech Service Routes Package"