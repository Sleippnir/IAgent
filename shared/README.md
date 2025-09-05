# Shared Library

## Utilidades Compartidas

### Logging y Tracing
```python
from shared.logging import get_logger
from shared.tracing import trace

logger = get_logger(__name__)

@trace
def my_function():
    logger.info("Executing function")
```

### Autenticación JWT
```python
from shared.auth import verify_token, create_token

# Crear token
token = create_token(user_id="123", role="admin")

# Verificar token
user = verify_token(token)
```

### Clientes de Base de Datos
```python
from shared.db import get_postgres_client, get_mongo_client, get_redis_client

# Postgres
db = get_postgres_client()
users = await db.fetch_all("SELECT * FROM users")

# MongoDB
mongo = get_mongo_client()
docs = await mongo.collection.find({})

# Redis
redis = get_redis_client()
await redis.set("key", "value")
```

### DTOs Comunes
```python
from shared.dto import (
    UserDTO,
    InterviewDTO,
    ResultDTO
)

user = UserDTO(
    id="123",
    email="user@example.com",
    role="admin"
)
```

### Errores Estándar
```python
from shared.errors import (
    NotFoundError,
    ValidationError,
    AuthenticationError
)

raise NotFoundError("User not found")
```

## Instalación

```bash
# Desde el directorio raíz
pip install -e ./shared
```

## Uso en Servicios

### requirements.txt
```
-e ../shared
```

### Ejemplo de Uso
```python
from fastapi import FastAPI
from shared.middleware import add_middleware
from shared.config import load_config

app = FastAPI()
config = load_config()

# Agregar middleware común
add_middleware(app)
```

## Configuración

### shared/config.py
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    POSTGRES_URI: str
    MONGO_URI: str
    REDIS_URI: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "RS256"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_TRACING: bool = True
```