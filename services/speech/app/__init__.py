#!/usr/bin/env python3
"""
Paquete principal de la aplicación Speech Service

Este paquete contiene toda la lógica de la aplicación para el servicio de speech,
incluyendo rutas, servicios y modelos.
"""

__version__ = "1.0.0"
__description__ = "Speech Service Application Package"
__author__ = "Speech Service Team"

# Configurar logging para evitar duplicación
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)