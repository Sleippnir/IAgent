#!/usr/bin/env python3
"""
Paquete de servicios del Speech Service

Este paquete contiene toda la lógica de negocio del servicio de speech.
"""

from .speech_service import SpeechService, speech_service

__all__ = [
    "SpeechService",
    "speech_service"
]

__version__ = "1.0.0"
__description__ = "Speech Service Business Logic Package"