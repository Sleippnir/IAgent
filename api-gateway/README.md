# API Gateway

## Responsabilidades

El API Gateway es responsable de:
- Enrutamiento y proxy de peticiones a microservicios
- Monitoreo de salud de servicios
- Balanceo de carga
- Registro y descubrimiento de servicios
- Manejo de errores y timeouts

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
docker build -t api-gateway .
```

2. Ejecutar el contenedor:
```bash
docker run -p 8000:8000 api-gateway
```

3. Verificar el estado:
```bash
curl http://localhost:8000/api/v1/healthz
```

## API Endpoints

### Health Check
- `GET /api/v1/healthz` - Estado del gateway y servicios

### Gestión de Servicios
- `POST /api/v1/services` - Registrar nuevo servicio
- `GET /api/v1/services` - Listar servicios registrados
- `GET /api/v1/services/{id}` - Obtener servicio por ID
- `PUT /api/v1/services/{id}` - Actualizar servicio
- `DELETE /api/v1/services/{id}` - Eliminar servicio

### Proxy
- `ANY /api/v1/proxy/{service_name}/{path}` - Proxy de peticiones a servicios