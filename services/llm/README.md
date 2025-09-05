# LLM Service

## Responsabilidades

El servicio LLM es responsable de:
- Procesamiento de lenguaje natural
- Generación de respuestas para entrevistas
- Gestión de prompts y parámetros
- Integración con modelos de lenguaje
- Procesamiento asíncrono de solicitudes

## Arquitectura

El servicio sigue los principios de Clean Architecture:

```
app/
├── domain/           # Reglas de negocio y entidades
├── application/      # Casos de uso
└── infrastructure/   # Frameworks, BD, API
```

## Ejecución con Docker

1. Construir la imagen:
```bash
docker build -t llm-service .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8001:8001 llm-service
```

3. Verificar el estado:
```bash
curl http://localhost:8001/api/v1/healthz
```

## API Endpoints

- `GET /api/v1/healthz` - Health check
- `POST /api/v1/prompts` - Crear prompt
- `GET /api/v1/prompts` - Listar prompts
- `GET /api/v1/prompts/{id}` - Obtener prompt