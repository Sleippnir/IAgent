# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_user_repository.py
# Repositorio real contra Supabase, para la tabla "users".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List, Any, Dict
from datetime import datetime 
import asyncpg # Driver asíncrono a Postgres (rápido, ideal para FastAPI).
from app.infrastructure.db import Database

# =======================
# Config de tabla/columnas
# =======================
TABLE = "users" # --> Nombre de la tabla en Supabase

COLS = [
    "id_user",
    "id_rol",
    "name_user",
    "email_user",
    "password",
    "timestamp_created",
]

# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =======================
# Adapter: DB row → dict “canónico”
# =======================
def _row_to_user(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir una fila de Posgres (asyncpg.Record) a un dict canónico del dominio.
    """
    if row is None:
        return None
    return {
        "id": row["id_user"],# --> id_user → id
        "role_id": row["id_rol"], # --> id_rol → role_id
        "name": row["name_user"], # --> name_user → name
        "email": row["email_user"], # --> email_user → email
        # --> Por seguridad, no devolvemos el hash de password en responses
        "created_at": row["timestamp_created"], # --> timestamp_created → created_at
    }

# =======================
# Helpers payload → parámetros
# =======================
# Orden de columnas tal como las vamos a pasar en los VALUES/SET para evitar confusiones.
INSERT_COLS = [
    "id_user",
    "id_rol",
    "name_user",
    "email_user",
    "password",
    "timestamp_created",
]

UPDATE_COLS = [
    "id_rol",
    "name_user",
    "email_user",
    "password",
]

def _payload_get(payload: Any, key: str, default=None):
    """
    Función que permite recibir un dict o un objeto Pydantic y leerle campos de forma uniforme.
    """
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _user_to_insert_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA INSERT respetando INSERT_COLS.
    Si no enviás id desde el dominio y lo genera la DB (uuid DEFAULT), podés poner None en id_candidate.
    """
    return [
        _payload_get(payload, "id", None),            # → id_user (puede ser None si DB genera)
        _payload_get(payload, "role_id", None),       # → id_rol
        _payload_get(payload, "name", None),          # → name_user
        _payload_get(payload, "email", None),         # → email_user
        _payload_get(payload, "password", None),      # → password (hash esperado)
        _payload_get(payload, "created_at", None),    # → timestamp_created (SQL usará now() si None)
    ]

def _user_to_update_params(payload: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA UPDATE respetando UPDATE_COLS.
    """
    return [
        _payload_get(payload, "role_id", None),  # id_rol
        _payload_get(payload, "name", None),     # name_user
        _payload_get(payload, "email", None),    # email_user
        _payload_get(payload, "password", None), # password (hash)
    ]

# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_user: str) -> Optional[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_user = $1
        LIMIT 1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_user)
    return _row_to_user(row)

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
    return [_row_to_user(r) for r in rows]

# =======================
# Crear (CREATE)
# =======================
async def create(user: Any) -> dict:
    params = _user_to_insert_params(user)
    sql = f"""
        INSERT INTO {TABLE} ({", ".join(INSERT_COLS)})
        VALUES ($1, $2, $3, $4, $5, COALESCE($6, now()))
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *params)
    return _row_to_user(row)

# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_user: str, updates: Any) -> Optional[dict]:
    params = _user_to_update_params(updates)  # [id_rol, name_user, email_user, password]
    sql = f"""
        UPDATE {TABLE}
        SET
          id_rol     = COALESCE($2, id_rol),
          name_user  = COALESCE($3, name_user),
          email_user = COALESCE($4, email_user),
          password   = COALESCE($5, password)
        WHERE id_user = $1
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_user, *params)
    return _row_to_user(row) if row else None

# =======================
# Borrar (DELETE)
# =======================
async def delete(id_user: str) -> bool:
    sql = f"DELETE FROM {TABLE} WHERE id_user = $1"
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_user)
    return result.upper().startswith("DELETE 1")
