# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_prompt_repository.py
# Repositorio real contra Supabase, para la tabla "prompts".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List, Any
import asyncpg
from app.infrastructure.db import Database  # pool global (lifespan)


# =======================
# Config de tabla/columnas
# =======================
TABLE = "prompts" # --> Nombre de la tabla en Supabase

COLS = [
    "id_prompts",
    "desc_prompt",
    "timestamp_created"
]

# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =================================
# Adapter: DB row → dict “canónico”
# =================================
def _row_to_prompt(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir columnas de DB a nombres "amigables" para API.
    """
    if row is None:
        return None
    return {
        "id": row["id_prompts"], # id_prompts → id
        "desc_prompt": row["desc_prompt"],
        "created_at": row["timestamp_created"], # timestamp_created → created_at
    }

def _payload_get(p: Any, k: str, default=None):
    """
    Función que permite recibir un dict o un objeto Pydantic y leerle campos de forma uniforme.
    """
    if isinstance(p, dict): return p.get(k, default)
    return getattr(p, k, default)

# =======================
# Helpers para INSERT/UPDATE (entidad/dict → parámetros SQL)
# =======================
# Orden de columnas tal como las vamos a pasar en los VALUES/SET para evitar confusiones.
INSERT_COLS = [
    "id_prompts",
    "desc_prompt",
    "timestamp_created"
]
UPDATE_COLS = [
    "desc_prompt"
]

def _to_insert_params(p: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA INSERT respetando INSERT_COLS.
    Si no enviás id desde el dominio y lo genera la DB (uuid DEFAULT), podés poner None en id_candidate.
    """
    return [
        _payload_get(p, "id", None),           # → id_prompts (puede ser None si DB genera)
        _payload_get(p, "desc_prompt", None),
        _payload_get(p, "created_at", None),   # → timestamp_created (SQL usará now() si None)
    ]

def _to_update_params(p: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA UPDATE respetando UPDATE_COLS.
    """
    return [
        _payload_get(p, "desc_prompt", None),
    ]


# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_prompts: str) -> Optional[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_prompts = $1 LIMIT 1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_prompts)
    return _row_to_prompt(row)

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
    return [_row_to_prompt(r) for r in rows]


# =======================
# Crear (CREATE)
# =======================
async def create(p: Any) -> dict:
    """
    Funcion que se encarga de crear un prompt.
    """
    params = _to_insert_params(p)
    sql = f"""
        INSERT INTO {TABLE} ({", ".join(INSERT_COLS)})
        VALUES ($1, $2, COALESCE($3, now()))
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *params)
    return _row_to_prompt(row)


# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_prompts: str, updates: Any) -> Optional[dict]:
    """
    Función que se encarga de actualizar un prompt por PK.
    Devuelve el registro actualizado (o None si no existe).
    """
    params = _to_update_params(updates)  # [desc_prompt]
    sql = f"""
        UPDATE {TABLE}
        SET desc_prompt = COALESCE($2, desc_prompt)
        WHERE id_prompts = $1
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_prompts, *params)
    return _row_to_prompt(row) if row else None


# =======================
# Borrar (DELETE)
# =======================
async def delete(id_prompts: str) -> bool:
    """
    Función que se encarga de eliminar un prompt por PK (borrado duro).
    Devuelve True si se borró 1 fila; False si no existía.
    """
    sql = f"""
        DELETE FROM {TABLE}
        WHERE id_prompts = $1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_prompts)
    return result.upper().startswith("DELETE 1")
