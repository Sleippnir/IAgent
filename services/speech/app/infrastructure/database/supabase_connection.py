import os
import logging
from supabase import create_client, Client
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseConnection:
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._url: Optional[str] = None
        self._key: Optional[str] = None
    
    def initialize(self, silent_env_error: bool = False) -> bool:
        """
        Inicializa la conexión con Supabase
        
        Args:
            silent_env_error: Si es True, no muestra logs de error solo para variables de entorno faltantes
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            # Obtener credenciales desde variables de entorno
            self._url = os.getenv('SUPABASE_URL')
            self._key = os.getenv('SUPABASE_ANON_KEY')
            
            if not self._url or not self._key:
                if not silent_env_error:
                    logger.error("❌ Variables de entorno SUPABASE_URL y SUPABASE_ANON_KEY son requeridas")
                return False
            
            # Crear cliente de Supabase
            self._client = create_client(self._url, self._key)
            
            # Verificar conexión
            if self.test_connection():
                logger.info("✅ Conexión con Supabase establecida exitosamente")
                return True
            else:
                logger.error("❌ Error al verificar la conexión con Supabase")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al inicializar Supabase: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Supabase
        
        Returns:
            bool: True si la conexión funciona, False en caso contrario
        """
        try:
            if not self._client:
                return False
            
            # Realizar una consulta simple para verificar la conexión
            # Intentar con la tabla 'interviews' que parece existir
            response = self._client.table('interviews').select('count', count='exact').limit(1).execute()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en test de conexión: {str(e)}")
            return False
    
    @property
    def client(self) -> Optional[Client]:
        """
        Obtiene el cliente de Supabase
        
        Returns:
            Optional[Client]: Cliente de Supabase si está inicializado
        """
        return self._client
    
    def is_connected(self) -> bool:
        """
        Verifica si hay una conexión activa
        
        Returns:
            bool: True si hay conexión, False en caso contrario
        """
        return self._client is not None

# Instancia global de la conexión
supabase_connection = SupabaseConnection()

def get_supabase_client(silent_env_error: bool = False) -> Optional[Client]:
    """
    Obtiene el cliente de Supabase inicializado
    
    Args:
        silent_env_error: Si es True, no muestra logs de error solo para variables de entorno faltantes
    
    Returns:
        Optional[Client]: Cliente de Supabase o None si no está inicializado
    """
    if not supabase_connection.is_connected():
        if not supabase_connection.initialize(silent_env_error=silent_env_error):
            return None
    
    return supabase_connection.client

def initialize_supabase(silent_env_error: bool = False) -> bool:
    """
    Inicializa la conexión con Supabase
    
    Args:
        silent_env_error: Si es True, no muestra logs de error solo para variables de entorno faltantes
    
    Returns:
        bool: True si la inicialización es exitosa
    """
    return supabase_connection.initialize(silent_env_error=silent_env_error)