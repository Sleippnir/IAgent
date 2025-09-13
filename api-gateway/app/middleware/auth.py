#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Middleware de Autenticación

Este middleware maneja la autenticación y autorización de las solicitudes.
Puede verificar tokens JWT, API keys, o implementar otros métodos de autenticación.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuración JWT (en producción, usar variables de entorno)
SECRET_KEY = "tu_clave_secreta_muy_segura_aqui"
ALGORITHM = "HS256"

# Esquema de seguridad Bearer
security = HTTPBearer()

class AuthMiddleware:
    """
    Middleware para manejar autenticación en el API Gateway
    """
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """
        Verifica y decodifica un token JWT
        
        Args:
            credentials: Credenciales de autorización HTTP
            
        Returns:
            Payload del token decodificado
            
        Raises:
            HTTPException: Si el token es inválido
        """
        try:
            # Decodificar el token JWT
            payload = jwt.decode(
                credentials.credentials, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verificar que el token contenga un usuario
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido: falta información del usuario",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"Error al verificar token JWT: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def verify_api_key(self, api_key: str) -> bool:
        """
        Verifica una API key
        
        Args:
            api_key: Clave de API a verificar
            
        Returns:
            True si la API key es válida, False en caso contrario
        """
        # Lista de API keys válidas (en producción, usar base de datos)
        valid_api_keys = [
            "api_key_desarrollo_123",
            "api_key_produccion_456",
            "api_key_testing_789"
        ]
        
        return api_key in valid_api_keys
    
    async def check_permissions(self, user_payload: dict, endpoint: str, method: str) -> bool:
        """
        Verifica si el usuario tiene permisos para acceder a un endpoint específico
        
        Args:
            user_payload: Información del usuario del token
            endpoint: Endpoint al que se intenta acceder
            method: Método HTTP (GET, POST, etc.)
            
        Returns:
            True si el usuario tiene permisos, False en caso contrario
        """
        # Obtener rol del usuario
        user_role = user_payload.get("role", "user")
        
        # Definir permisos por rol
        permissions = {
            "admin": ["*"],  # Acceso total
            "user": ["GET:/api/v1/core/*", "POST:/api/v1/llm/*"],  # Acceso limitado
            "guest": ["GET:/api/v1/core/health"]  # Solo endpoints públicos
        }
        
        user_permissions = permissions.get(user_role, [])
        
        # Verificar si tiene acceso total
        if "*" in user_permissions:
            return True
        
        # Verificar permisos específicos
        endpoint_permission = f"{method}:{endpoint}"
        for permission in user_permissions:
            if permission.endswith("*"):
                # Verificar permisos con wildcard
                if endpoint_permission.startswith(permission[:-1]):
                    return True
            elif permission == endpoint_permission:
                return True
        
        return False

# Instancia global del middleware
auth_middleware = AuthMiddleware()

async def authenticate_request(request: Request) -> Optional[dict]:
    """
    Función auxiliar para autenticar una solicitud
    
    Args:
        request: Objeto de solicitud HTTP
        
    Returns:
        Información del usuario autenticado o None si no está autenticado
    """
    # Verificar si la ruta requiere autenticación
    public_endpoints = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    if request.url.path in public_endpoints:
        return None
    
    # Verificar token Bearer
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        try:
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=authorization.split(" ")[1]
            )
            return await auth_middleware.verify_token(credentials)
        except HTTPException:
            pass
    
    # Verificar API Key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        if await auth_middleware.verify_api_key(api_key):
            return {"sub": "api_user", "role": "user", "auth_method": "api_key"}
    
    # Si no hay autenticación válida para endpoints protegidos
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticación requerida",
        headers={"WWW-Authenticate": "Bearer"},
    )