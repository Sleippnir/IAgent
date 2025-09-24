# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_candidate_repository.py
# Este repositorio habla con la DB de Supabase (motor Postgres) usando SQL real.
# Usa el pool creado por app.infrastructure.db (inicializado en el lifespan del Core).
# La cadena de conexión viene de POSTGRES_URI en el .env :contentReference[oaicite:0]{index=0}
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*



from __future__ import annotations 
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncpg  # Driver asíncrono a Postgres (rápido, ideal para FastAPI).
from app.infrastructure.db import Database  # Nuestro pool global (lifespan lo abre/cierra).
# Entidad de dominio Candidate e interfaz CandidateRepository::
from ....domain.entities.candidate import Candidate
from ....domain.repositories.candidate_repository import CandidateRepository

# =======================
# Config de tabla/columnas
# =======================
TABLE = "candidates"  # --> Nombre de la tabla en Supabase

# Columnas reales en tu diagrama (ajustá si cambian nombres exactos):
COLS = [
    "id_candidate",
    "name",
    "last_name",
    "phone_num",
    "email",
    "linkedin_url",
    "age",
    "resume",
    "timestamp_created",
]

# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =======================
# Adapter: DB row → entidad/dict
# =======================
def _row_to_candidate(row: asyncpg.Record) -> dict:
    """
    # Traduce una fila de Postgres (asyncpg.Record) a un dict “canónico” del dominio.
    # Si más adelante se define la entidad Pydantic como `Candidate`, se puede devolver `Candidate(**data)`.
    """
    if row is None:
        return None
    
    data = {
        "id": row["id_candidate"], # Renombramos id_candidate → id (más cómodo en API)
        "name": row["name"],
        "last_name": row["last_name"],
        "phone_num": row["phone_num"],
        "email": row["email"],
        "linkedin_url": row["linkedin_url"],
        "resume": row["resume"], # bytea en DB; si no lo usás aún, lo dejamos tal cual.
        "created_at": row["timestamp_created"]# Renombramos timestamp_created → created_at (coherencia)
    }
    return data

# =======================
# Helpers para INSERT/UPDATE (entidad/dict → parámetros SQL)
# =======================
# Orden de columnas tal como las vamos a pasar en los VALUES/SET para evitar confusiones.
INSERT_COLS = [
    "id_candidate",
    "name",
    "last_name",
    "phone_num",
    "email",
    "linkedin_url",
    "resume",
    "timestamp_created",
]

UPDATE_COLS = [
    "name",
    "last_name",
    "phone_num",
    "email",
    "linkedin_url",
    "resume",
]

def _payload_get(payload: Any, key: str, default=None):
    """
     Función que permite recibir un dict o un objeto Pydantic y leerle campos de forma uniforme.
    """
    if isinstance(payload, dict):
        return payload.get(key, default) 
    return getattr(payload, key, default) # Para modelos Pydantic/objetos: getattr con default.

def _candidate_to_insert_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA INSERT respetando INSERT_COLS.
    Si no enviás id desde el dominio y lo genera la DB (uuid DEFAULT), podés poner None en id_candidate.
    """
    return [
        _payload_get(payload, "id", None), # REVISAR → Dependiendo quien genera el ID del id_candidate
        _payload_get(payload, "name", None),
        _payload_get(payload, "last_name", None),
        _payload_get(payload, "phone_num", None),
        _payload_get(payload, "email", None),
        _payload_get(payload, "linkedin_url", None),
        _payload_get(payload, "resume", None),
        _payload_get(payload, "created_at", None),# → timestamp_created (si None, SQL usará now())
    ]

def _candidate_to_update_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA UPDATE respetando UPDATE_COLS.
    """
    return [
        _payload_get(payload, "name", None),
        _payload_get(payload, "last_name", None),
        _payload_get(payload, "phone_num", None),
        _payload_get(payload, "email", None),
        _payload_get(payload, "linkedin_url", None),
        _payload_get(payload, "resume", None),
    ]

# ==================================
# Métodos de lectura: get() y list()
# ==================================

async def get(id_candidate: str) -> Optional[dict]:
    """
    Función que se encarga de traer un candidato por PK (id_candidate).
    Devuelve dict “canónico” vía _row_to_candidate(...) o None si no existe.
    """
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_candidate = $1
        LIMIT 1
    """
    pool = Database.pool()  # Aquí tomamos el pool creado por lifespan
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_candidate)
    return _row_to_candidate(row) if row else None

async def list(limit: int = 100, offset: int = 0) -> List[dict]:
    """
    Funcion que se encarga de listar candidatos con paginación simple.
    ORDER por timestamp_created DESC para ver lo más nuevo primero.
    """
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        ORDER BY timestamp_created DESC
        LIMIT $1 OFFSET $2
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, limit, offset)
    return [_row_to_candidate(r) for r in rows]


# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_candidate: str, updates: Any) -> Optional[dict]:
    """
    Función que se encarga de actualizar un candidato por PK.
    Usa COALESCE: si un campo viene None, se conserva el valor actual en DB (parcial estilo PATCH).
    Devuelve el registro actualizado (o None si no existe).
    """
    # Orden de parámetros para SET según UPDATE_COLS
    params = _candidate_to_update_params(updates)  # [name, last_name, phone_num, email, linkedin_url, resume]

    sql = f"""
        UPDATE {TABLE}
        SET
            name         = COALESCE($2, name),
            last_name    = COALESCE($3, last_name),
            phone_num    = COALESCE($4, phone_num),
            email        = COALESCE($5, email),
            linkedin_url = COALESCE($6, linkedin_url),
            resume       = COALESCE($7, resume)
        WHERE id_candidate = $1
        RETURNING {SELECT_LIST}
    """
    # $1 es la PK; $2..$7 son los posibles cambios (COALESCE mantiene el valor anterior si viene None).
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_candidate, *params)

    # Si no hay fila (id inexistente), devolvemos None
    return _row_to_candidate(row) if row else None

# =======================
# Borrar (DELETE)
# =======================
async def delete(id_candidate: str) -> bool:
    """
    Función que se encarga de eliminar un candidato por PK (borrado duro).
    Devuelve True si se borró 1 fila; False si no existía.
    """
    sql = f"DELETE FROM {TABLE} WHERE id_candidate = $1"
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_candidate)
    #asyncpg retorna textos tipo "DELETE 1" / "DELETE 0"
    return result.upper().startswith("DELETE 1")

