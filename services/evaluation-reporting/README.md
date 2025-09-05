# Evaluation & Reporting Service

## Responsabilidades
- Evaluación automática de entrevistas técnicas
- Análisis de respuestas y competencias:
  * Precisión técnica
  * Claridad de comunicación
  * Profundidad de conocimiento
  * Capacidad de resolución de problemas
- Generación de reportes detallados
- Exportación en múltiples formatos (PDF, DOCX, HTML)
- Integración con bases de datos para persistencia
- Procesamiento asíncrono de evaluaciones

## Levantar el Servicio

### Requisitos
- Docker instalado
- PostgreSQL accesible
- MongoDB accesible
- Redis accesible
- Variables de entorno configuradas
- wkhtmltopdf instalado (para PDF)

### Construir la Imagen
```bash
docker build -t ia-interviews/evaluation-reporting .
```

### Ejecutar el Contenedor
```bash
docker run -d \
  --name evaluation-reporting \
  -p 8005:8005 \
  -v $(pwd):/app \
  -v reports:/app/reports \
  --env-file .env \
  ia-interviews/evaluation-reporting
```

### Verificar el Servicio
```bash
curl http://localhost:8005/healthz
```

## Puerto
- 8005 (HTTP)

## Consumo de Eventos

### Redis Streams
```
interview:{id}:answers      # Respuestas para evaluación
interview:{id}:evaluation   # Resultados de evaluación
```

### Consumer Groups
```
evaluation-group    # Procesamiento de respuestas
reporting-group     # Generación de reportes
```

## Persistencia

### MongoDB
- Transcripciones completas
- Resultados de evaluación
- Reportes generados

### PostgreSQL
- Metadatos de entrevistas
- Estadísticas agregadas
- Referencias a documentos

## Variables de Entorno
```
# Database
MONGO_URI=mongodb://mongo:27017/eval
POSTGRES_URI=postgresql://user:pass@postgres:5432/eval
REDIS_URI=redis://redis:6379/0

# LLM Service
LLM_SERVICE_URL=http://llm:8004

# Export Settings
PDF_TEMPLATE_DIR=/app/templates
MAX_REPORT_PAGES=50

# Stream Processing
BATCH_SIZE=10
PROCESSING_TIMEOUT=30
```

## Criterios de Evaluación
- Precisión técnica
- Claridad de comunicación
- Profundidad de conocimiento
- Resolución de problemas
- Experiencia relevante

## Formatos de Reporte
- PDF ejecutivo
- JSON detallado
- Dashboard metrics

## Puerto
- HTTP: 8005