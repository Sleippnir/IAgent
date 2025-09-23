import redis
import json
import os
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Cliente Redis simple y limpio"""
    
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.password = os.getenv('REDIS_PASSWORD', None)
        
        self._client = None
    
    @property
    def client(self) -> redis.Redis:
        """Obtiene el cliente Redis (singleton)"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_timeout=5
            )
        return self._client
    
    def ping(self) -> bool:
        """Verifica conexión con Redis"""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Guarda valor en Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor de Redis"""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Error getting {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Elimina clave de Redis"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si existe la clave"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Error checking {key}: {e}")
            return False

# Instancia global
redis_client = RedisClient()