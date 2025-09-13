# API Gateway

## Descripción

Este API Gateway actúa como punto de entrada único para todos los microservicios de la aplicación. Proporciona funcionalidades de enrutamiento, autenticación, monitoreo y agregación de datos.

## Características Principales

- 🚀 **Enrutamiento Inteligente**: Redirige automáticamente las solicitudes a los microservicios correspondientes
- 🔐 **Autenticación y Autorización**: Soporte para JWT y API Keys
- 📊 **Monitoreo y Logging**: Registro detallado de todas las solicitudes
- 🏥 **Health Checks**: Verificación del estado de todos los servicios
- 🔄 **Agregación de Datos**: Combina respuestas de múltiples servicios
- ⚡ **Alto Rendimiento**: Construido con FastAPI y operaciones asíncronas

## Estructura del Proyecto

```
api-gateway/
├── main.py                 # Archivo principal del API Gateway
├── requirements.txt        # Dependencias de Python
├── .env.example           # Ejemplo de variables de entorno
├── README.md              # Este archivo
└── app/
    ├── middleware/
    │   └── auth.py        # Middleware de autenticación
    ├── routes/
    │   └── example.py     # Rutas de ejemplo
    └── utils/
        └── helpers.py     # Funciones auxiliares
```

## Instalación y Configuración

### 1. Instalar Dependencias

```bash
# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus configuraciones
```

### 3. Ejecutar el API Gateway

```bash
# Modo desarrollo (con recarga automática)
python main.py

# O usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Uso del API Gateway

### Endpoints Principales

#### 1. Información General
```http
GET /
```
Devuelve información básica del API Gateway y servicios disponibles.

#### 2. Verificación de Salud
```http
GET /health
```
Verifica que el API Gateway esté funcionando correctamente.

#### 3. Proxy a Microservicios
```http
GET|POST|PUT|DELETE /api/v1/{service_name}/{path}
```
Redirige automáticamente las solicitudes al microservicio correspondiente.

**Ejemplos:**
```bash
# Solicitud al servicio 'orchestrator'
curl http://localhost:8000/api/v1/orchestrator/speech/info

# Se redirige automáticamente a:
# http://localhost:8001/speech/info

# Solicitud al servicio 'core'
curl http://localhost:8000/api/v1/core/users

# Se redirige automáticamente a:
# http://localhost:8002/api/v1/users
```

### Endpoints de Ejemplo

#### 1. Verificar Todos los Servicios
```http
GET /api/v1/example/health-all
```
Verifica el estado de salud de todos los microservicios registrados.

#### 2. Agregar Datos de Múltiples Servicios
```http
GET /api/v1/example/aggregate-data
```
Obtiene y combina datos de varios microservicios en una sola respuesta.

#### 3. Envío Masivo (Broadcast)
```http
POST /api/v1/example/broadcast
```
Envía la misma solicitud a todos los microservicios disponibles.

#### 4. Información de Servicio Específico
```http
GET /api/v1/example/service-info/{service_name}
```
Obtiene información detallada de un microservicio específico.

## Autenticación

El API Gateway soporta múltiples métodos de autenticación:

### 1. Token JWT (Bearer Token)
```bash
curl -H "Authorization: Bearer tu_jwt_token_aqui" \
     http://localhost:8000/api/v1/core/protected-endpoint
```

### 2. API Key
```bash
curl -H "X-API-Key: tu_api_key_aqui" \
     http://localhost:8000/api/v1/llm/generate
```

### Endpoints Públicos
Los siguientes endpoints no requieren autenticación:
- `/` (información general)
- `/health` (verificación de salud)
- `/docs` (documentación de la API)
- `/redoc` (documentación alternativa)

## Configuración de Servicios

Los microservicios se configuran en el archivo `main.py`:

```python
SERVICES = {
    "orchestrator": "http://localhost:8001",
    "core": "http://localhost:8002",
    "llm": "http://localhost:8003",
    "speech": "http://localhost:8004",
    "evaluation": "http://localhost:8005"
}
```

### Agregar un Nuevo Servicio

1. Añadir la URL del servicio al diccionario `SERVICES`
2. Asegurarse de que el servicio tenga un endpoint `/health`
3. Reiniciar el API Gateway

## Monitoreo y Logging

El API Gateway registra automáticamente:
- Todas las solicitudes HTTP
- Tiempos de respuesta
- Códigos de estado
- Errores de conexión
- Estadísticas de uso

### Ver Estadísticas
Las estadísticas se pueden obtener a través de los endpoints de ejemplo o consultando los logs.

## Desarrollo y Extensión

### Agregar Nuevas Rutas

1. Crear un nuevo archivo en `app/routes/`
2. Definir un router con FastAPI
3. Importar y registrar el router en `main.py`

```python
# En app/routes/mi_nueva_ruta.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/mi-ruta")

@router.get("/ejemplo")
async def mi_endpoint():
    return {"mensaje": "¡Hola desde mi nueva ruta!"}

# En main.py
from app.routes.mi_nueva_ruta import router as mi_router
app.include_router(mi_router)
```

### Agregar Middleware Personalizado

1. Crear el middleware en `app/middleware/`
2. Registrarlo en `main.py`

```python
# En main.py
from app.middleware.mi_middleware import MiMiddleware
app.add_middleware(MiMiddleware)
```

## Solución de Problemas

### Problemas Comunes

1. **Error 503 - Servicio no disponible**
   - Verificar que el microservicio esté ejecutándose
   - Comprobar la URL en la configuración de `SERVICES`
   - Revisar los logs del microservicio

2. **Error 401 - No autorizado**
   - Verificar que el token JWT sea válido
   - Comprobar que la API Key esté en la lista de claves válidas
   - Revisar los permisos del usuario

3. **Timeouts**
   - Aumentar el valor de `HTTP_TIMEOUT` en las variables de entorno
   - Verificar la conectividad de red
   - Optimizar el rendimiento del microservicio

### Logs de Depuración

Para habilitar logs más detallados:

```bash
# Establecer nivel de log en variables de entorno
export LOG_LEVEL=DEBUG

# O modificar directamente en main.py
logging.basicConfig(level=logging.DEBUG)
```

## Producción

### Consideraciones de Seguridad

1. **Variables de Entorno**: Nunca hardcodear secretos en el código
2. **CORS**: Configurar orígenes específicos en lugar de `*`
3. **Rate Limiting**: Implementar límites de velocidad
4. **HTTPS**: Usar siempre HTTPS en producción
5. **Logs**: No registrar información sensible

### Despliegue

```bash
# Usando Gunicorn para producción
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# O usando Docker
docker build -t api-gateway .
docker run -p 8000:8000 api-gateway
```

## Contribución

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.