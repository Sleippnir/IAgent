#!/usr/bin/env python3
"""
Servicio de Speech - Lógica de negocio

Este módulo contiene la lógica principal para el procesamiento de voz y texto.
Recibe transmisiones del orchestrator via gRPC, guarda contenido localmente
y reenvía respuestas procesadas sin latencia adicional.
"""

import asyncio
import json
import logging
import os
from .pipecat_service import run_bot
from typing import Dict, Any, Optional
from aiortc.contrib.media import MediaRelay, MediaRecorder
from pipecat.transports.network.webrtc_connection import IceServer, SmallWebRTCConnection
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)

# Definir la ruta para la carpeta storage
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")

# Crear la carpeta storage si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapa global para almacenar conexiones WebRTC activas
pcs_map = {}

class SpeechService:
    """
    Servicio principal para procesamiento de speech.
    
    Maneja procesamiento de voz y texto a través de API REST.
    """
    
    def __init__(self):
        """Inicializar el servicio de speech"""
        self.service_name = "Speech Service"
        self.version = "1.0.0"
        self.active_sessions = {}
        self.active_connections = {}
        self.media_relay = MediaRelay()
        
        logger.info(f"Inicializando {self.service_name} v{self.version}")
        logger.info("Servicio configurado para procesamiento de voz y texto via API REST")
    
    async def get_service_info(self) -> Dict[str, Any]:
        """
        Obtener información del servicio.
        
        Returns:
            Dict con información del servicio
        """
        logger.info("Obteniendo información del servicio")
        
        return {
            "service": self.service_name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "rest-api",
                "audio-processing",
                "text-processing",
                "file-storage",
                "real-time-response"
            ],
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "root": "/"
            },
            "active_sessions": len(self.active_sessions),
            "storage_location": "media_storage/"
        }
    
    async def offer(self, pc_id, sdp, type, background_tasks: BackgroundTasks):
        # Configurar servidores ICE
        ice_servers = [IceServer(urls=["stun:stun.l.google.com:19302"])]
        
        if pc_id and pc_id in pcs_map:
            pipecat_connection = pcs_map[pc_id]
            logger.info(f"Reusing existing connection for pc_id: {pc_id}")
            await pipecat_connection.renegotiate(sdp, type)
        else:
            pipecat_connection = SmallWebRTCConnection(ice_servers)
            await pipecat_connection.initialize(sdp, type)

            @pipecat_connection.event_handler("closed")
            async def handle_disconnected(webrtc_connection: SmallWebRTCConnection):
                logger.info(f"Discarding peer connection for pc_id: {webrtc_connection.pc_id}")
                pcs_map.pop(webrtc_connection.pc_id, None)

            background_tasks.add_task(run_bot, pipecat_connection)

        answer = pipecat_connection.get_answer()
        # Updating the peer connection inside the map
        pcs_map[answer["pc_id"]] = pipecat_connection

        return answer
    
# Instancia global del servicio
speech_service = SpeechService()