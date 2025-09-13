#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funciones de Utilidad

Este archivo contiene funciones auxiliares y utilidades comunes
que pueden ser utilizadas en diferentes partes del API Gateway.
"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from fastapi import Request

logger = logging.getLogger(__name__)

class RequestLogger:
    """
    Clase para registrar y analizar las solicitudes HTTP
    """
    
    def __init__(self):
        self.request_history: List[Dict] = []
        self.max_history = 1000  # Mantener solo las últimas 1000 solicitudes
    
    def log_request(self, request: Request, response_time: float, status_code: int):
        """
        Registra una solicitud HTTP
        
        Args:
            request: Objeto de solicitud HTTP
            response_time: Tiempo de respuesta en milisegundos
            status_code: Código de estado HTTP de la respuesta
        """
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "response_time_ms": round(response_time, 2),
            "status_code": status_code,
            "request_id": self.generate_request_id(request)
        }
        
        self.request_history.append(request_data)
        
        # Mantener solo las últimas solicitudes
        if len(self.request_history) > self.max_history:
            self.request_history = self.request_history[-self.max_history:]
        
        # Log según el nivel de severidad
        if status_code >= 500:
            logger.error(f"Error del servidor: {request.method} {request.url} -> {status_code} ({response_time:.2f}ms)")
        elif status_code >= 400:
            logger.warning(f"Error del cliente: {request.method} {request.url} -> {status_code} ({response_time:.2f}ms)")
        else:
            logger.info(f"Solicitud exitosa: {request.method} {request.url} -> {status_code} ({response_time:.2f}ms)")
    
    def generate_request_id(self, request: Request) -> str:
        """
        Genera un ID único para la solicitud
        
        Args:
            request: Objeto de solicitud HTTP
            
        Returns:
            ID único de la solicitud
        """
        # Crear un hash basado en timestamp, IP y URL
        data = f"{time.time()}{request.client.host if request.client else 'unknown'}{request.url}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las solicitudes registradas
        
        Returns:
            Diccionario con estadísticas de las solicitudes
        """
        if not self.request_history:
            return {"message": "No hay solicitudes registradas"}
        
        # Calcular estadísticas básicas
        total_requests = len(self.request_history)
        response_times = [req["response_time_ms"] for req in self.request_history]
        status_codes = [req["status_code"] for req in self.request_history]
        
        # Estadísticas de tiempo de respuesta
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Contar códigos de estado
        status_count = {}
        for code in status_codes:
            status_count[code] = status_count.get(code, 0) + 1
        
        # Contar métodos HTTP
        method_count = {}
        for req in self.request_history:
            method = req["method"]
            method_count[method] = method_count.get(method, 0) + 1
        
        return {
            "total_requests": total_requests,
            "average_response_time_ms": round(avg_response_time, 2),
            "min_response_time_ms": min_response_time,
            "max_response_time_ms": max_response_time,
            "status_codes": status_count,
            "http_methods": method_count,
            "success_rate": round((sum(1 for code in status_codes if code < 400) / total_requests) * 100, 2)
        }

class ServiceHealthChecker:
    """
    Clase para verificar el estado de salud de los microservicios
    """
    
    def __init__(self, services: Dict[str, str]):
        self.services = services
        self.health_cache = {}
        self.cache_duration = 30  # Cachear resultados por 30 segundos
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Verifica el estado de salud de un servicio específico
        
        Args:
            service_name: Nombre del servicio a verificar
            
        Returns:
            Diccionario con el estado del servicio
        """
        # Verificar cache
        cache_key = f"health_{service_name}"
        if cache_key in self.health_cache:
            cached_result, timestamp = self.health_cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return cached_result
        
        if service_name not in self.services:
            return {
                "service": service_name,
                "status": "not_configured",
                "message": "Servicio no configurado"
            }
        
        service_url = self.services[service_name]
        
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result = {
                "service": service_name,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time, 2),
                "status_code": response.status_code,
                "url": service_url,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar en cache
            self.health_cache[cache_key] = (result, time.time())
            
            return result
            
        except Exception as e:
            logger.error(f"Error verificando salud de {service_name}: {e}")
            result = {
                "service": service_name,
                "status": "error",
                "message": str(e),
                "url": service_url,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar en cache (incluso errores, para evitar spam)
            self.health_cache[cache_key] = (result, time.time())
            
            return result

def format_response(data: Any, success: bool = True, message: str = "") -> Dict[str, Any]:
    """
    Formatea una respuesta estándar para el API Gateway
    
    Args:
        data: Datos a incluir en la respuesta
        success: Indica si la operación fue exitosa
        message: Mensaje descriptivo opcional
        
    Returns:
        Diccionario con formato estándar de respuesta
    """
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return response

def validate_service_name(service_name: str, available_services: List[str]) -> bool:
    """
    Valida si un nombre de servicio es válido
    
    Args:
        service_name: Nombre del servicio a validar
        available_services: Lista de servicios disponibles
        
    Returns:
        True si el servicio es válido, False en caso contrario
    """
    return service_name in available_services

def sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Sanitiza los headers HTTP removiendo información sensible
    
    Args:
        headers: Diccionario de headers HTTP
        
    Returns:
        Headers sanitizados
    """
    # Headers que no deben ser reenviados
    sensitive_headers = {
        "authorization",
        "cookie",
        "x-api-key",
        "x-auth-token"
    }
    
    sanitized = {}
    for key, value in headers.items():
        if key.lower() not in sensitive_headers:
            sanitized[key] = value
    
    return sanitized

def calculate_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Calcula el tiempo de espera para reintentos usando backoff exponencial
    
    Args:
        attempt: Número de intento (empezando en 1)
        base_delay: Tiempo base de espera en segundos
        max_delay: Tiempo máximo de espera en segundos
        
    Returns:
        Tiempo de espera en segundos
    """
    delay = base_delay * (2 ** (attempt - 1))
    return min(delay, max_delay)

# Instancias globales
request_logger = RequestLogger()