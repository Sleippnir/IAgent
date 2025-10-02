# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_techqa_job_repository.py
# Repositorio real contra Supabase, para la tabla "technical_questions_answers_jobs".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List
import asyncpg
from app.infrastructure.db import Database

# =======================
# Config de tabla/columnas
# =======================
TABLE = "technical_questions_answers_jobs" # --> Nombre de la tabla en Supabase
COLS = [
    "id_job",
    "id_tech_question_ans",
    "timestamp_created"
]
# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)


# =================================
# Adapter: DB row → dict “canónico”
# =================================
def _row_to_link(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir columnas de DB a nombres "amigables" para API.
    """
    if row is None:
        return None
    return {
        "job_id": row["id_job"],
        "techqa_id": row["id_tech_question_ans"],
        "created_at": row["timestamp_created"],
    }

# =================================
# Adapter: Crear Vinculo
# =================================
async def link(job_id: str, techqa_id: str) -> dict:
    """
    Función que se encarga de implementar un upsert sobre la tabla de relacion Job-TechQa usando una clave unica compesta.
    Garantiza idempotencia: crea el vinculo si no existe o retorna el existente, y 
    siempre devuelve la representación de la relacion mediante RETURNING.
    """
    sql = f"""
        INSERT INTO {TABLE} (id_job, id_tech_question_ans, timestamp_created)
        VALUES ($1, $2, now())
        ON CONFLICT (id_job, id_tech_question_ans) DO UPDATE SET id_job = EXCLUDED.id_job
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, job_id, techqa_id)
    return _row_to_link(row)

# =================================
# Adapter: Elimina Vinculo
# =================================
async def unlink(job_id: str, techqa_id: str) -> bool:
    """
    Función que se encarga de eliminar la relacion especifica y retorna un booleano indicando si efectivamente se borró una fila.
    """
    sql = f"""
        DELETE FROM {TABLE}
        WHERE id_job = $1 AND id_tech_question_ans = $2
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, job_id, techqa_id)
    return result.upper().startswith("DELETE 1")

async def list_by_job(job_id: str, limit: int = 200, offset: int = 0) -> List[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_job = $1
        ORDER BY timestamp_created DESC
        LIMIT $2 OFFSET $3
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, job_id, limit, offset)
    return [_row_to_link(r) for r in rows]

async def list_by_techqa(techqa_id: str, limit: int = 200, offset: int = 0) -> List[dict]:
    sql = f"""
        SELECT {SELECT_LIST}
        FROM {TABLE}
        WHERE id_tech_question_ans = $1
        ORDER BY timestamp_created DESC
        LIMIT $2 OFFSET $3
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, techqa_id, limit, offset)
    return [_row_to_link(r) for r in rows]
