# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_role_repository.py
# Repositorio real contra Supabase, para la tabla rol_users (roles). CRUD básico (list/get).
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List
import asyncpg
from app.infrastructure.db import Database


# =======================
# Config de tabla/columnas
# =======================
TABLE = "rol_users" # --> Nombre de la tabla en Supabase

COLS = [
    "id_rol",
    "role_name",
    "timestamp_created"
]
# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

def _row_to_role(row: asyncpg.Record) -> Optional[dict]:
    if row is None:
        return None
    return {
        "id": row["id_rol"],
        "role_name": row["role_name"],
        "created_at": row["timestamp_created"],
    }


# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_rol: str) -> Optional[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_rol = $1
        LIMIT 1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_rol)
    return _row_to_role(row)

async def list(limit: int = 100, offset: int = 0) -> List[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        ORDER BY timestamp_created DESC
        LIMIT $1 OFFSET $2
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(limit, offset)
    return [_row_to_role(r) for r in rows]
