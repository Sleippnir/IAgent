# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_techqa_repository.py
# Repositorio real contra Supabase, para la tabla "technical_questions_answers".
# SQL explícito + pool de asyncpg del lifespan.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Optional, List, Any
import asyncpg
from app.infrastructure.db import Database # pool global (lifespan)


# =======================
# Config de tabla/columnas
# =======================
TABLE = "technical_questions_answers" # --> Nombre de la tabla en Supabase
COLS = [
    "id_tech_question_ans",
    "question",
    "answer",
    "timestamp_created"
]
# SELECT list armado explícito para mantener orden y evitar '*'
SELECT_LIST = ", ".join(COLS)

# =================================
# Adapter: DB row → dict “canónico”
# =================================
def _row_to_techqa(row: asyncpg.Record) -> Optional[dict]:
    """
    Función que se encarga de traducir columnas de DB a nombres "amigables" para API.
    """
    if row is None:
        return None
    return {
        "id": row["id_tech_question_ans"], # --> id_tech_question_ans → id
        "question": row["question"],
        "answer": row["answer"],
        "created_at": row["timestamp_created"],
    }

# =======================
# Helpers para INSERT/UPDATE (entidad/dict → parámetros SQL)
# =======================
# Orden de columnas tal como las vamos a pasar en los VALUES/SET para evitar confusiones.
INSERT_COLS = [
    "id_tech_question_ans",
    "question",
    "answer",
    "timestamp_created"
]
UPDATE_COLS = [
    "question",
    "answer"
]

def _payload_get(p: Any, k: str, default=None):
    """
    Función que permite recibir un dict o un objeto Pydantic y leerle campos de forma uniforme.
    """
    if isinstance(p, dict): return p.get(k, default)
    return getattr(p, k, default)


def _to_insert_params(p: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA INSERT respetando INSERT_COLS.
    Si no enviás id desde el dominio y lo genera la DB (uuid DEFAULT), podés poner None en id_candidate.
    """
    return [
        _payload_get(p, "id", None),
        _payload_get(p, "question", None),
        _payload_get(p, "answer", None),
        _payload_get(p, "created_at", None),
    ]

def _to_update_params(p: Any) -> list:
    """
    Función que se encarga de armar la lista de parámetros PARA UPDATE respetando UPDATE_COLS.
    """
    return [
        _payload_get(p, "question", None),
        _payload_get(p, "answer", None),
    ]


# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
async def get(id_techqa: str) -> Optional[dict]:
    sql = f"""
    SELECT {SELECT_LIST}
    FROM {TABLE}
    WHERE id_tech_question_ans = $1 LIMIT 1
"""
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_techqa)
    return _row_to_techqa(row)

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
    return [_row_to_techqa(r) for r in rows]


# =======================
# Crear (CREATE)
# =======================
async def create(p: Any) -> dict:
    """
    Funcion que se encarga de crear un "techincal questions answers".
    """
    params = _to_insert_params(p)
    sql = f"""
        INSERT INTO {TABLE} ({", ".join(INSERT_COLS)})
        VALUES ($1, $2, $3, COALESCE($4, now()))
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, *params)
    return _row_to_techqa(row)


# =======================
# Actualizar (UPDATE)
# =======================
async def update(id_techqa: str, updates: Any) -> Optional[dict]:
    """
    Función que se encarga de actualizar un "techincal questions answers" por PK.
    Devuelve el registro actualizado (o None si no existe).
    """
    params = _to_update_params(updates)  # [question, answer]
    sql = f"""
        UPDATE {TABLE}
        SET
          question = COALESCE($2, question),
          answer   = COALESCE($3, answer)
        WHERE id_tech_question_ans = $1
        RETURNING {SELECT_LIST}
    """
    pool = Database.pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, id_techqa, *params)
    return _row_to_techqa(row) if row else None

# =======================
# Borrar (DELETE)
# =======================
async def delete(id_techqa: str) -> bool:
    """
    Función que se encarga de eliminar un "techincal questions answers" por PK (borrado duro).
    Devuelve True si se borró 1 fila; False si no existía.
    """
    sql = f"DELETE FROM {TABLE} WHERE id_tech_question_ans = $1"
    pool = Database.pool()
    async with pool.acquire() as conn:
        result = await conn.execute(sql, id_techqa)
    return result.upper().startswith("DELETE 1")
