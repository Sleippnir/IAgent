# Orchestrator Service

## Responsabilidades
- Gestión de conexiones en tiempo real (WebSocket/WebRTC)
- Coordinación del flujo de comunicación entre servicios:
  * Speech-to-Text para transcripción de audio
  * LLM para procesamiento de respuestas
  * Text-to-Speech para generación de audio
- Control de estado de entrevistas activas
- Gestión de eventos mediante Redis Streams
- Manejo de sesiones y reconexiones

## Levantar el Servicio

### Requisitos
- Docker instalado
- Redis accesible
- Servicios STT, LLM y TTS configurados
- Variables de entorno configuradas

### Construir la Imagen
```bash
docker build -t ia-interviews/orchestrator .
```

### Ejecutar el Contenedor
```bash
docker run -d \
  --name orchestrator \
  -p 8002:8002 \
  -v $(pwd):/app \
  --env-file .env \
  ia-interviews/orchestrator
```

### Verificar el Servicio
```bash
curl http://localhost:8002/healthz
```

## Puerto
- 8002 (HTTP/WebSocket/WebRTC)