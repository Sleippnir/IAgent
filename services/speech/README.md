# Speech Service

## Responsabilidades

El servicio Speech es responsable de:
- Procesamiento de audio en tiempo real
- Conversión de voz a texto (STT)
- Conversión de texto a voz (TTS)
- Gestión de archivos de audio
- Procesamiento de streaming de audio

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
docker build -t speech-service .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8002:8002 speech-service
```

3. Verificar el estado:
```bash
curl http://localhost:8002/api/v1/healthz
```

## API Endpoints

- `GET /api/v1/healthz` - Health check
- `POST /api/v1/audio` - Subir archivo de audio
- `GET /api/v1/audio` - Listar archivos de audio
- `GET /api/v1/audio/{id}` - Obtener archivo de audio