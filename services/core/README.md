# Core Service

## Responsabilidades

El servicio Core es responsable de:
- Gestión central de entrevistas técnicas
- Administración de datos principales (entrevistas, candidatos, posiciones)
- Persistencia en MongoDB
- Coordinación con otros servicios
- Implementación de la lógica de negocio principal

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
docker build -t core-service .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 core-service
```

3. Verificar el estado:
```bash
curl http://localhost:8000/api/v1/healthz
```

## API Endpoints

- `GET /api/v1/healthz` - Health check
- `POST /api/v1/interviews` - Crear entrevista
- `GET /api/v1/interviews` - Listar entrevistas
- `GET /api/v1/interviews/{id}` - Obtener entrevista
- `PATCH /api/v1/interviews/{id}` - Actualizar estado