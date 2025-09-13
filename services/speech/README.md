# Speech Service

## Descripción

Este es un servicio de speech simplificado que contiene solo endpoints de ejemplo para demostrar la interacción entre los archivos de rutas y servicios.

## Estructura del Proyecto

```
speech/
├── main.py                     # Punto de entrada principal
├── requirements.txt            # Dependencias de Python
├── README.md                   # Este archivo
└── app/
    ├── __init__.py            # Inicialización del paquete
    ├── routes/
    │   ├── __init__.py        # Inicialización de rutas
    │   └── speech_routes.py   # Rutas HTTP (solo ejemplos)
    └── services/
        ├── __init__.py        # Inicialización de servicios
        └── speech_service.py  # Lógica de negocio (solo ejemplos)
```

## Endpoints Disponibles

### 1. Información del Servicio
```http
GET /api/v1/speech/info
```
Devuelve información detallada del servicio de speech.

### 2. Verificación de Salud
```http
GET /api/v1/speech/health
```
Verifica que el servicio esté funcionando correctamente.

### 3. Salud General
```http
GET /health
```
Endpoint básico de verificación de salud.

### 4. Información Raíz
```http
GET /
```
Información básica del servicio.

## Instalación y Ejecución

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el Servicio
```bash
# Desarrollo
python main.py

# O usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

## Arquitectura de Ejemplo

Este servicio demuestra:

1. **Separación de responsabilidades**:
   - `main.py`: Configuración de la aplicación FastAPI
   - `routes/`: Definición de endpoints HTTP
   - `services/`: Lógica de negocio

2. **Inyección de dependencias**:
   - Los servicios se inyectan en las rutas usando `Depends()`
   - Permite testing y modularidad

3. **Manejo de errores**:
   - Try-catch en los endpoints
   - Logging de errores
   - Respuestas HTTP apropiadas

4. **Logging**:
   - Logging estructurado en toda la aplicación
   - Diferentes niveles de log

## Uso como Ejemplo

Este servicio sirve como plantilla para entender:
- Cómo estructurar un microservicio con FastAPI
- Cómo separar rutas y lógica de negocio
- Cómo implementar inyección de dependencias
- Cómo manejar errores y logging

## Desarrollo

Para agregar nuevas funcionalidades:

1. **Agregar nueva lógica**: Crear métodos en `SpeechService`
2. **Agregar nuevas rutas**: Crear endpoints en `speech_routes.py`
3. **Mantener la separación**: Las rutas solo manejan HTTP, los servicios manejan la lógica

## Puerto

El servicio se ejecuta en el puerto **8004** por defecto.