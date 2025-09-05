# Imagen base
FROM python:3.9-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/opt/poetry/bin:$PATH"

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias
RUN poetry install --no-root --no-dev

# Copiar código fuente
COPY . .

# Instalar el paquete actual
RUN poetry install --no-dev

# Exponer puerto
EXPOSE 8001

# Comando de inicio
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]