.PHONY: up down logs ps build clean test

# Variables
COMPOSE = docker compose
SERVICES = gateway core orchestrator speech llm evaluation-reporting

# Comandos principales
up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

# Construir servicios
build:
	$(COMPOSE) build $(SERVICES)

# Ver logs
logs:
	$(COMPOSE) logs -f

# Ver logs de un servicio específico
log-%:
	$(COMPOSE) logs -f $*

# Estado de servicios
ps:
	$(COMPOSE) ps

# Limpiar volúmenes
clean:
	$(COMPOSE) down -v

# Reiniciar un servicio específico
restart-%:
	$(COMPOSE) restart $*

# Ejecutar tests
test:
	$(COMPOSE) run --rm core pytest
	$(COMPOSE) run --rm orchestrator pytest
	$(COMPOSE) run --rm speech pytest
	$(COMPOSE) run --rm llm pytest
	$(COMPOSE) run --rm evaluation-reporting pytest

# Generar claves JWT
gen-keys:
	mkdir -p keys
	openssl genrsa -out keys/private.pem 2048
	openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# Configuración inicial
init: gen-keys
	cp -n .env.example .env

# Ayuda
help:
	@echo "Comandos disponibles:"
	@echo "  make up              - Iniciar todos los servicios"
	@echo "  make down            - Detener todos los servicios"
	@echo "  make build           - Construir todos los servicios"
	@echo "  make logs            - Ver logs de todos los servicios"
	@echo "  make log-<service>   - Ver logs de un servicio específico"
	@echo "  make ps              - Ver estado de los servicios"
	@echo "  make clean           - Limpiar volúmenes"
	@echo "  make restart-<service> - Reiniciar un servicio específico"
	@echo "  make test            - Ejecutar tests"
	@echo "  make init            - Configuración inicial"
	@echo "  make gen-keys        - Generar claves JWT"