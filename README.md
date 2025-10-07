# Plataforma de Entrevistas con IA

Plataforma de entrevistas automatizadas basada en microservicios que utiliza IA para realizar y evaluar entrevistas en tiempo real.

## Arquitectura

### Servicios

- **API Gateway**: Punto de entrada único, maneja autenticación y enrutamiento.
- **Core**: Gestión de usuarios, roles, invitaciones y entrevistas.
- **Speech**: Provee servicios de STT y TTS en tiempo real.
- **Evaluation & Reporting**: Evaluación y generación de reportes.

### Infraestructura

- **Redis**: Streams, Cache y almacenamiento de invitaciones
- **PostgreSQL**: Usuarios, roles y metadatos

## Requisitos

- Docker y Docker Compose
- Claves de API (OpenAI/Anthropic/etc)
- ~20GB de espacio en disco

## Configuración Inicial

1. Clonar el repositorio:
```bash
git clone https://github.com/your-org/ia-interviews.git
cd ia-interviews
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus claves y configuraciones
```

3. Generar claves JWT:
```bash
# Crear directorio para claves
mkdir keys

# Generar par de claves RSA
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

## Iniciar Servicios

### Usando Docker Compose

```bash
# Construir e iniciar todos los servicios
docker compose up -d --build

# Ver logs
docker compose logs -f

# Detener servicios
docker compose down
```

### Verificar Estado

```bash
# Verificar estado de los servicios
docker compose ps

# Verificar logs de un servicio específico
docker compose logs -f service_name
```

## Endpoints Principales

- Gateway: http://localhost:8080
- Core: http://localhost:8001
- Speech: http://localhost:8003
- Evaluation: http://localhost:8005

## Monitoreo

Cada servicio expone endpoints de healthcheck y métricas:

```bash
# Healthcheck
curl http://localhost:8080/healthz

# Métricas
curl http://localhost:8080/metrics
```

## Desarrollo

### Estructura del Proyecto
```
.
├── gateway/           # API Gateway + WAF
├── services/
│   ├── core/         # Auth, Users, RBAC
│   ├── speech/      # STT/TTS Services
│   └── evaluation/  # Scoring & Reports
├── infra/           # DB init scripts
```

### Bibliotecas Compartidas

```bash
# Instalar shared lib en modo desarrollo
pip install -e ./shared
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a bases de datos**
   - Verificar credenciales en .env
   - Confirmar que los servicios están corriendo
   - Revisar logs específicos

2. **Problemas con GPU**
   - Verificar instalación de NVIDIA Container Toolkit
   - Confirmar drivers actualizados
   - Revisar logs de speech service

3. **Errores de JWT**
   - Verificar existencia de keys/
   - Confirmar permisos de archivos
   - Validar configuración en .env

## Contribuir

1. Fork el repositorio
2. Crear branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request
