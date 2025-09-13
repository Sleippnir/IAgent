# Dockerfile para API Gateway
# Este archivo permite crear una imagen Docker del API Gateway

# Usar imagen base oficial de Python
FROM python:3.11-slim

# Establecer información del mantenedor
LABEL maintainer="Tu Nombre <tu.email@ejemplo.com>"
LABEL description="API Gateway para microservicios"
LABEL version="1.0.0"

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV API_GATEWAY_HOST=0.0.0.0
ENV API_GATEWAY_PORT=8000

# Comando de verificación de salud
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]