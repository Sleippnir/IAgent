# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_generalqa_repository.py
# Repositorio real contra Supabase, para la tabla "general_questions_answers".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List, Any
import asyncpg
from app.infrastructure.db import Database

# =======================
# Config de tabla/columnas
# =======================
TABLE = "general_questions_answers"  # --> Nombre de la tabla en Supabase

COLS = [
    "id_gral_question_ans",
    "question",
    "answer",
    "timestamp_created"
]

# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =======================
# Adapter: DB row → dict “canónico”
# =======================
def _row_to_generalqa(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir una fila de Posgres (asyncpg.Record) a un dict canónico del dominio.
    """
    if row is None:
        return None
    return {
        "id": row["id_gral_question_ans"], # id_gral_question_ans → id
        "question": row["question"],
        "answer": row["answer"],
        "created_at": row["timestamp_created"], # timestamp_created → created_at
    }

# =======================
# Helpers payload → parámetros
# =======================
def _pget(p: Any, k: str, default=None):
    if isinstance(p, dict): return p.get(k, default)
    return getattr(p, k, default)

# Orden de columnas tal como las vamos a pasar en los VALUES/SET para evitar confusiones.
INSERT_COLS = [
    "id_gral_question_ans",
    "question",
    "answer",
    "timestamp_created"
]
UPDATE_COLS = [
    "question",
    "answer"
]

def _to_insert_params(p: Any) -> list:
    return [
        _pget(p, "id", None), 
        _pget(p, "question", None),
        _pget(p, "answer", None),
        _pget(p, "created_at", None),
    ]

def _to_update_params(p: Any) -> list:
    return [
        _pget(p, "question", None),
        _pget(p, "answer", None),
    ]

# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_gralqa: str) -> Optional[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_gral_question_ans = $1 LIMIT 1
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_gralqa)
    return _row_to_generalqa(row)

async def list(limit: int = 100, offset: int = 0, q: Optional[str] = None) -> List[dict]:
    pool = Database.pool()
    if q:
        sql = f"""
            SELECT {SELECT_LIST}
            FROM {TABLE}
            WHERE question ILIKE '%' || $3 || '%' OR answer ILIKE '%' || $3 || '%'
            ORDER BY timestamp_created DESC
            LIMIT $1 OFFSET $2
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, limit, offset, q)
    else:
        sql = f"""
            SELECT {SELECT_LIST}
            FROM {TABLE}
            ORDER BY timestamp_created DESC
            LIMIT $1 OFFSET $2
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, limit, offset)
    return [_row_to_generalqa(r) for r in rows]

# =======================
# Crear (CREATE)
# =======================
async def create(p: Any) -> dict:
    params = _to_insert_params(p)
    sql = f"""
        INSERT INTO {TABLE} ({", ".join(INSERT_COLS)})
        VALUES ($1, $2, $3, COALESCE($4, now()))
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *params)
    return _row_to_generalqa(row)

# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_gralqa: str, updates: Any) -> Optional[dict]:
    params = _to_update_params(updates)  # [question, answer]
    sql = f"""
        UPDATE {TABLE}
        SET
          question = COALESCE($2, question),
          answer   = COALESCE($3, answer)
        WHERE id_gral_question_ans = $1
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_gralqa, *params)
    return _row_to_generalqa(row) if row else None

# =======================
# Borrar (DELETE)
# =======================
async def delete(id_gralqa: str) -> bool:
    sql = f"DELETE FROM {TABLE} WHERE id_gral_question_ans = $1"
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_gralqa)
    return result.upper().startswith("DELETE 1")
