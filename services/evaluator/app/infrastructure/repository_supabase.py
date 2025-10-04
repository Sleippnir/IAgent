# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/app/infrastructure/repository_supabase.py
# Arma el contexto sin crear views ni tocar schemas.
# interviews --> jobs --> prompts --> transcript (full_conversations o messages)
# Devuelve dict con 5 claves exactas: interview_id, system_prompt, rubric, jd, full_transcript
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import os, json
from postgrest.exceptions import APIError


# NICO --> SDK Supabase
from supabase import create_client, Client

# NICO --> Contrato base
from .repository import EvaluatorRepository


# --------------- Helpers de tiempo / util ---------------
def _ts(dt: Optional[str]) -> str:
    """
    # NICO --> Normaliza fechas a 'YYYY-MM-DD HH:MM' (para transcript de messages).
    """
    if not dt:
        return ""
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(dt)

def _now_iso() -> str:
    """
    # NICO --> Timestamp ISO en UTC (para evaluation_updated_at si lo seteamos desde app).
    """
    return datetime.now(timezone.utc).isoformat()

# --- Helper: intentar extraer texto de context_data (jsonb) ---
def _extract_transcript_from_context_data(ctx_obj: Any) -> Optional[str]:
    # NICO --> Si viene como string JSON, parseamos
    if isinstance(ctx_obj, str):
        try:
            ctx_obj = json.loads(ctx_obj)
        except Exception:
            return None

    if not isinstance(ctx_obj, dict):
        return None

    # 1) Claves directas frecuentes
    for k in ("full_text", "fullTranscript", "transcript", "content", "text"):
        v = ctx_obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, list):
            joined = "\n".join([str(x) for x in v if isinstance(x, (str, int, float))])
            if joined.strip():
                return joined.strip()

    # 2) Conversación como lista de mensajes
    msgs = ctx_obj.get("messages") or ctx_obj.get("conversation") or ctx_obj.get("turns")
    if isinstance(msgs, list):
        lines = []
        for m in msgs:
            if isinstance(m, dict):
                role = (m.get("role") or "").strip()
                content = (m.get("content") or "").strip()
                created = _ts(m.get("created_at") or m.get("ts"))
                prefix = f"[{created}] " if created else ""
                rolep  = f"{role}: " if role else ""
                line = f"{prefix}{rolep}{content}".strip()
                if line:
                    lines.append(line)
        if lines:
            return "\n".join(lines)

    return None


# --------------- Clase SupabaseRepository ---------------
class SupabaseRepository(EvaluatorRepository):
    """
    Implementa el contrato sobre Supabase:
      - interviews -> id_job
      - jobs -> jd
      - prompts -> últimos por tipo ('evaluator_system' y 'evaluator_rubric')
      - transcript -> primero en interview_full_conversations; si no, desde interview_messages
    """

    # --------------- Client init ---------------
    def __init__(self) -> None:
        """
        # NICO --> Crea cliente leyendo del .env:
        #          SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (o SUPABASE_ANON_KEY).
        """
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError("Faltan SUPABASE_URL y/o SUPABASE_SERVICE_ROLE_KEY en el entorno (.env).")
        self.sb: Client = create_client(url, key)

    # --------------- Lecturas base ---------------
    def _get_interview_row(self, interview_id: str) -> Dict[str, Any]:
        """
        # NICO --> Valida que exista la entrevista y devuelve (id_interview, id_job).
        """
        # NICO --> Intentamos comparar con INT (columna es integer); si falla casteamos a str
        rows = []
        try:
            res = (self.sb.table("interviews")
                        .select("id_interview,id_job")
                        .eq("id_interview", int(str(interview_id).strip()))
                        .limit(1)
                        .execute())
            rows = res.data or []
        except Exception:
            res = (self.sb.table("interviews")
                        .select("id_interview,id_job")
                        .eq("id_interview", str(interview_id).strip())
                        .limit(1)
                        .execute())
            rows = res.data or []

        if not rows:
            raise ValueError(f"No existe interviews.id_interview={interview_id}")
        return rows[0]

    def _get_job_description(self, job_id: Any) -> str:
        """
        # NICO --> Devuelve jobs.description o "".
        """
        if job_id is None:
            return ""
        rows = []
        try:
            res = (self.sb.table("jobs")
                        .select("id_job,description")
                        .eq("id_job", int(job_id))
                        .limit(1)
                        .execute())
            rows = res.data or []
        except Exception:
            res = (self.sb.table("jobs")
                        .select("id_job,description")
                        .eq("id_job", str(job_id))
                        .limit(1)
                        .execute())
            rows = res.data or []
        if not rows:
            raise ValueError(f"No existe jobs.id_job={job_id}")
        return rows[0].get("description") or ""

    def _get_prompt_latest(self, prompt_type: str) -> Optional[str]:
        """
        # NICO --> Último contenido por tipo en 'prompts'. Si no hay, None.
        """
        try:
            q = (self.sb.table("prompts")
                     .select("content,updated_at,created_at,id")
                     .eq("prompt_type", prompt_type)
                     .order("updated_at", desc=True)
                     .order("created_at", desc=True)
                     .order("id", desc=True)
                     .limit(1))
            res = q.execute()
            rows = res.data or []
            return rows[0]["content"] if rows else None
        except Exception:
            return None

    # --------------- Transcript: full_conversations primero ---------------
    # NICO --> IMPORTANTE: agregá este import arriba del archivo
# from postgrest.exceptions import APIError

    def _get_transcript_from_full_conversations(self, interview_id: str) -> Optional[str]:
        """
        NICO --> Soporta ambos esquemas sin pedir columnas que podrían no existir.
        1) SELECT "*" y ordenar por created_at si existe; si no, por id; si no, sin orden.
        2) Intenta extraer en este orden: full_text -> context_data (heurística) -> claves alternativas.
        """
        table = self.sb.table("interview_full_conversations")

        candidates = [
            ("interview_id", str(interview_id).strip()),
        ]
        try:
            candidates.append(("interview_id", int(str(interview_id).strip())))
        except Exception:
            pass
        try:
            candidates.append(("id_interview", int(str(interview_id).strip())))
        except Exception:
            pass
        candidates.append(("id_interview", str(interview_id).strip()))

        for col, val in candidates:
            rows = []
            # NICO --> 1) Ordenar por created_at si existe
            try:
                res = (table.select("*").eq(col, val).order("created_at", desc=True).limit(1).execute())
                rows = res.data or []
            except APIError as e:
                # 42703 = columna no existe (created_at)
                # Reintentamos con 'id' y luego sin orden.
                try:
                    res = (table.select("*").eq(col, val).order("id", desc=True).limit(1).execute())
                    rows = res.data or []
                except APIError:
                    res = (table.select("*").eq(col, val).limit(1).execute())
                    rows = res.data or []
            except Exception:
                # Último intento, sin orden
                try:
                    res = (table.select("*").eq(col, val).limit(1).execute())
                    rows = res.data or []
                except Exception:
                    rows = []

            if not rows:
                continue

            row = rows[0]

            # 1) full_text directo
            ft = row.get("full_text")
            if isinstance(ft, str) and ft.strip():
                print(f"[DEBUG] transcript from full_text (row={row.get('id')})")
                return ft.strip()

            # 2) context_data -> heurística
            ctx = row.get("context_data")
            if ctx is not None:
                t = _extract_transcript_from_context_data(ctx)
                if t:
                    print(f"[DEBUG] transcript from context_data (row={row.get('id')})")
                    return t

            # 3) compat: otras claves si existieran en tu tabla
            for k in ("full_transcript", "content", "transcript", "text"):
                v = row.get(k)
                if isinstance(v, str) and v.strip():
                    print(f"[DEBUG] transcript from alt key '{k}' (row={row.get('id')})")
                    return v.strip()

        return None


    # --------------- Transcript: fallback messages ---------------
    def _get_transcript_from_messages(self, interview_id: str) -> Optional[str]:
        """
        NICO --> Si la tabla 'interview_messages' no existe, retorna None sin romper.
        """
        try:
            # Intento INT
            res = (self.sb.table("interview_messages")
                        .select("role,content,created_at")
                        .eq("interview_id", int(str(interview_id).strip()))
                        .order("created_at", desc=False)
                        .execute())
            rows: List[Dict[str, Any]] = res.data or []
        except APIError as e:
            # PGRST205 = tabla no existe en el schema cache
            if getattr(e, "code", None) == "PGRST205":
                print("[DEBUG] table 'interview_messages' not found; skipping messages fallback")
                return None
            # Reintentamos con string; si vuelve a fallar por tabla, ignoramos
            try:
                res = (self.sb.table("interview_messages")
                            .select("role,content,created_at")
                            .eq("interview_id", str(interview_id).strip())
                            .order("created_at", desc=False)
                            .execute())
                rows = res.data or []
            except APIError as e2:
                if getattr(e2, "code", None) == "PGRST205":
                    print("[DEBUG] table 'interview_messages' not found; skipping messages fallback")
                    return None
                return None
            except Exception:
                return None
        except Exception:
            # Si falla por otro motivo, probamos string una vez
            try:
                res = (self.sb.table("interview_messages")
                            .select("role,content,created_at")
                            .eq("interview_id", str(interview_id).strip())
                            .order("created_at", desc=False)
                            .execute())
                rows = res.data or []
            except Exception:
                return None

        if not rows:
            return None

        lines: List[str] = []
        for r in rows:
            role = r.get("role", "unknown")
            content = (r.get("content") or "").strip()
            created = _ts(r.get("created_at"))
            lines.append(f"[{created}] {role}: {content}" if created else f"{role}: {content}")
        print(f"[DEBUG] transcript assembled from messages (count={len(lines)})")
        return "\n".join(lines)


    # --------------- Implementación: armar contexto ---------------
    async def get_interview_context(self, interview_id: str) -> Dict[str, Any]:
        """
        Orquesta:
          1) interviews -> id_job
          2) jobs -> jd
          3) prompts -> system_prompt & rubric (o defaults)
          4) transcript -> full_conversations o messages
          5) retorna dict con 5 claves para Interview.from_dict
        """
        # 1) entrevista
        irow = self._get_interview_row(interview_id)
        job_id = irow.get("id_job")

        # 2) job description
        jd = self._get_job_description(job_id) if job_id is not None else ""

        # 3) prompts (últimos por tipo) o defaults
        system_prompt = self._get_prompt_latest("evaluator_system") or \
                        "You are an expert technical evaluator. Output concise, rubric-based evaluation."
        rubric = self._get_prompt_latest("evaluator_rubric") or \
                 "Criteria: Problem Solving, Python, APIs/HTTP, Databases/SQL, Communication. Rate 1-5 and justify briefly. End with Overall Verdict: Hire/No Hire."

        # 4) transcript
        full_transcript = (self._get_transcript_from_full_conversations(interview_id)
                           or self._get_transcript_from_messages(interview_id))
        if not full_transcript:
            raise ValueError(f"No hay transcript para interview_id={interview_id} (ni en full_conversations ni en messages).")

        # 5) respuesta final
        return {
            "interview_id": str(interview_id),
            "system_prompt": system_prompt,
            "rubric": rubric,
            "jd": jd,
            "full_transcript": full_transcript,
        }

    # --------------- Persistencia: resultados ---------------
    async def save_evaluation_results(self, interview_id: str, results: Dict[str, Any]) -> None:
        """
        Intenta guardar en 'interviews':
          - evaluation_results_json (JSONB, preferido)
          - evaluation_status='done'
          - evaluation_updated_at=now()
        Si falla (columna o permisos), cae a fallback local.
        """
        from pathlib import Path

        # NICO --> Intento A: JSON completo en una sola columna (preferido)
        payloads = [
            {
                "evaluation_status": "done",
                "evaluation_updated_at": _now_iso(),
                "evaluation_results_json": results,
            },
            # NICO --> Intento B: textos sueltos (por si existe ese diseño alternativo)
            {
                "evaluation_status": "done",
                "evaluation_updated_at": _now_iso(),
                "evaluation_1_text": results.get("evaluation_1"),
                "evaluation_2_text": results.get("evaluation_2"),
                "evaluation_3_text": results.get("evaluation_3"),
            },
        ]

        last_error = None
        for payload in payloads:
            try:
                (self.sb.table("interviews")
                        .update(payload)
                        .eq("id_interview", int(str(interview_id).strip()))
                        .execute())
                print(f"[Evaluator] DB results saved for interview={interview_id}")
                return
            except Exception as e:
                last_error = e
                # NICO --> probamos con str si falla el cast
                try:
                    (self.sb.table("interviews")
                            .update(payload)
                            .eq("id_interview", str(interview_id).strip())
                            .execute())
                    print(f"[Evaluator] DB results saved for interview={interview_id} (string match)")
                    return
                except Exception as e2:
                    last_error = e2

        # Fallback local (igual que mock)
        try:
            base_dir = Path(__file__).resolve().parents[2]  # .../services/evaluator
            out_dir = base_dir / "out" / "evaluations"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{interview_id}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[Evaluator] Local results saved: {out_path} (DB error: {last_error})")
        except Exception as e:
            print(f"[Evaluator] ERROR saving results locally: {e} (previous DB error: {last_error})")

    # --------------- Persistencia: estado ---------------
    async def mark_evaluation_status(self, interview_id: str, status: str, error: Optional[str] = None) -> None:
        """
        Estados sugeridos: queued | running | done | error
        Intenta actualizar columnas; si falla, escribe fallback local.
        """
        from pathlib import Path

        payload = {
            "evaluation_status": status,
            "evaluation_updated_at": _now_iso(),
        }
        # NICO --> No asumimos 'evaluation_error' en DB; si querés guardarlo, podés agregar la columna luego.
        # if error:
        #     payload["evaluation_error"] = str(error)

        try:
            (self.sb.table("interviews")
                    .update(payload)
                    .eq("id_interview", int(str(interview_id).strip()))
                    .execute())
            print(f"[Evaluator] Status updated in DB: {payload}")
            return
        except Exception:
            try:
                (self.sb.table("interviews")
                        .update(payload)
                        .eq("id_interview", str(interview_id).strip())
                        .execute())
                print(f"[Evaluator] Status updated in DB (string match): {payload}")
                return
            except Exception as e2:
                print(f"[Evaluator] WARNING: status not updated in DB. Using local status. Error: {e2}")

        # Fallback local
        try:
            base_dir = Path(__file__).resolve().parents[2]  # .../services/evaluator
            out_dir = base_dir / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            status_path = out_dir / f"status_{interview_id}.json"
            status_payload = {"interview_id": str(interview_id), "status": status}
            if error:
                status_payload["error"] = str(error)
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(status_payload, f, ensure_ascii=False, indent=2)
            print(f"[Evaluator] Local status saved: {status_payload}")
        except Exception as e:
            print(f"[Evaluator] ERROR saving local status: {e}")
