# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_job_repository.py
# Repositorio real contra Supabase, para la tabla "jobs".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List, Any, Dict
from datetime import datetime

import asyncpg  # Driver asíncrono Postgres
from app.infrastructure.db import Database  # Pool global

# =======================
# Config de tabla/columnas
# =======================
TABLE = "jobs"  # --> Nombre de la tabla en Supabase

COLS = [
    "id_job",
    "job_role",
    "description",
    "timestamp_created",
]

# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =================================
# Adapter: DB row → dict “canónico”
# =================================
def _row_to_job(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir columnas de DB a nombres "amigables" para API.
    """
    if row is None:
        return None
    return {
        "id": row["id_job"], # --> id_job → id
        "job_role": row["job_role"],
        "description": row["description"],
        "created_at": row["timestamp_created"], # timestamp_created → created_at
    }

# ===============================
# Helpers de payload → parámetros
# ===============================
INSERT_COLS = [
    "id_job",
    "job_role",
    "description",
    "timestamp_created",
]

UPDATE_COLS = [
    "job_role",
    "description",
]

def _payload_get(payload: Any, key: str, default=None):
    """
    Función que permite recibir un dict o un objeto Pydantic y leerle campos de forma uniforme.
    """
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)

def _job_to_insert_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA INSERT respetando INSERT_COLS.
    Si no enviás id desde el dominio y lo genera la DB (uuid DEFAULT), podés poner None en id_candidate.
    """
    return [
        _payload_get(payload, "id", None),       
        _payload_get(payload, "job_role", None),
        _payload_get(payload, "description", None),
        _payload_get(payload, "created_at", None),  
    ]

def _job_to_update_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA UPDATE respetando UPDATE_COLS.
    """
    return [
        _payload_get(payload, "job_role", None),
        _payload_get(payload, "description", None),
    ]


# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_job: str) -> Optional[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_job = $1
        LIMIT 1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_job)
    return _row_to_job(row)

async def list(limit: int = 100, offset: int = 0) -> List[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        ORDER BY timestamp_created DESC
        LIMIT $1 OFFSET $2
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, limit, offset)
    return [_row_to_job(r) for r in rows]

# =======================
# Crear (CREATE)
# =======================
async def create(job: Any) -> dict:
    """
    Funcion que se encarga de crear un job.
    """
    params = _job_to_insert_params(job)
    sql = f"""
        INSERT INTO {TABLE} ({", ".join(INSERT_COLS)})
        VALUES ($1, $2, $3, COALESCE($4, now()))
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *params)
    return _row_to_job(row)



# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_job: str, updates: Any) -> Optional[dict]:
    """
    Función que se encarga de actualizar un job por PK.
    Devuelve el registro actualizado (o None si no existe).
    """
    params = _job_to_update_params(updates)  # [job_role, description]
    sql = f"""
        UPDATE {TABLE}
        SET
          job_role   = COALESCE($2, job_role),
          description = COALESCE($3, description)
        WHERE id_job = $1
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_job, *params)
    return _row_to_job(row) if row else None

# =======================
# Borrar (DELETE)
# =======================
async def delete(id_job: str) -> bool:
    """
    Función que se encarga de eliminar un job por PK (borrado duro).
    Devuelve True si se borró 1 fila; False si no existía.
    """
    sql = f"DELETE FROM {TABLE} WHERE id_job = $1"
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_job)
    return result.upper().startswith("DELETE 1")
