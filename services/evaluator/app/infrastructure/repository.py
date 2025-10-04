# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/app/infrastructure/repository.py
# Este bloque se encarga de configurar el Contrato base del Evaluator + Implementacion MOCK (archivos locales).
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
from __future__ import annotations
from typing import Dict, Any, Optional
from pathlib import Path
import json

# --> Intentamos importar el loader (si esta disponible), importe relativo ya que esta en el mismo paquete infrastructure.
try:
    from .llm_provider import load_interview_from_source  # type: ignore
    _HAS_LOADER = True # --> Flag: Tenemos loader externo disponible? 
except Exception:
    _HAS_LOADER = False # --> Flag: no hay loader, usamos lectura manual de JSON


class EvaluatorRepository:
    """
    Contrato base del repositorio del Evaluator.

    Este contrato define tres responsabilidades:
      1) get_interview_context(interview_id) -> Dict[str, Any]
            Obtiene el CONTEXTO mínimo para instanciar Interview
            (system_prompt, rubric, jd, full_transcript, interview_id)

      2) save_evaluation_results(interview_id, results) -> None
            Persiste las evaluaciones del LLM (hoy: archivo o DB si existe)

      3) mark_evaluation_status(interview_id, status, error?) -> None
            Marca estado ('queued'|'running'|'done'|'error') para que el front vea progreso
    """
    async def get_interview_context(self, interview_id: str) -> Dict[str, Any]: # --> devuelve el contexto mínimo para instanciar Interview
        # --> Método abstracto: las subclases deben implementarlo
        raise NotImplementedError

    async def save_evaluation_results(self, interview_id: str, results: Dict[str, Any]) -> None: # --> persiste evaluaciones (por ahora a disco)
        # --> Método abstracto: las subclases deben implementarlo
        raise NotImplementedError

    async def mark_evaluation_status(self, interview_id: str, status: str, error: Optional[str] = None) -> None: # --> marca estado (running, done, error) para que el front pueda ver progreso
        # --> Método abstracto: las subclases deben implementarlo
        raise NotImplementedError


class FileMockRepository(EvaluatorRepository):
    """
    Implementación MOCK para desarrollo local.

    Lee el contexto desde `services/evaluator/examples/<interview_id>.json`
    y guarda outputs en `services/evaluator/out/`.

    Métodos que implementa:
      - get_interview_context -> Dict con 5 claves exactas
      - save_evaluation_results -> JSON en out/evaluations/<id>.json
      - mark_evaluation_status -> JSON en out/status_<id>.json
    """

    def __init__(self, examples_dir: Optional[Path] = None, out_dir: Optional[Path] = None) -> None:
        # --> Calcula la base del servicio evaluator a partir de ESTE archivo.
        base_dir = Path(__file__).resolve().parents[2]   # --> / "services" / "evaluator"
        self.examples_dir = examples_dir or (base_dir / "examples") # --> Carpeta con ejemplos de contexto
        self.out_dir = out_dir or (base_dir / "out") # --> Carpeta de salida (status + resultados)

        # --> Asegura estructura de carpetas (no falla si ya existen)
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "evaluations").mkdir(parents=True, exist_ok=True)

    async def get_interview_context(self, interview_id: str) -> Dict[str, Any]:
        """
        Devuelve un dict con las 5 claves mínimas:
          - interview_id, system_prompt, rubric, jd, full_transcript

        Estrategia:
          1) Si existe load_interview_from_source("file", <nombre.json>), la usamos
             (busca en varias rutas y devuelve Interview -> .to_dict()).
          2) Sino, leemos el JSON directo desde `examples/<interview_id>.json`.

        Ejemplo de mapeo:
          interview_id="demo-001" --> examples/demo-001.json
        """
        filename = f"{interview_id}.json" # --> Armamos el nombre del archivo de ejemplo
        json_path = self.examples_dir / filename # --> Resolvemos ruta final en examples/

        if _HAS_LOADER:
            # --> Usamos el loader de Marco: ya conoce varias ubicaciones ("examples", "storage", etc.)
            interview_obj = load_interview_from_source("file", filename) # --> Devuelve Interview
            return interview_obj.to_dict() # --> Normalizamos a dict de 5 claves

        # --> Fallback: lectura manual del JSON
        if not json_path.exists():
            raise FileNotFoundError(f"Mock file not found: {json_path}") # --> Error claro si no existe

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f) # --> Parseo del JSON a dict

        # --> Validación mínima para evitar dicts incompletos
        required = {"interview_id", "system_prompt", "rubric", "jd", "full_transcript"}
        missing = required - set(data.keys())
        if missing:
            raise KeyError(f"Missing keys in mock JSON: {missing}") # --> Faltan claves: aborta con detalle

        return data # --> Dict listo para Interview.from_dict

    async def save_evaluation_results(self, interview_id: str, results: Dict[str, Any]) -> None:
        """
        Guarda resultados de evaluación en disco (JSON legible).

        Flujo típico:
          - Se llama después de run_evaluations(interview)
          - Escribe/actualiza: out/evaluations/<interview_id>.json
        """
        out_path = self.out_dir / "evaluations" / f"{interview_id}.json" # --> Calcula la ruta final del archivo de resultados para esta entrevista. 
        # --> Se encarga de abrir el archivo en modo escritoria 'w', sobreescribe si ya existe.
        #      y vuelca el dict 'results' como Json.
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"[Evaluator] Results saved: {out_path}")  # --> Log simple a consola

    async def mark_evaluation_status(self, interview_id: str, status: str, error: Optional[str] = None) -> None:
        """
        Publica un estado simple de la evaluación para consulta rápida
        mientras no haya WebSocket/eventos.

        Estados típicos: "queued", "running", "done", "error".
        """
        status_payload = {"interview_id": interview_id, "status": status} # --> Arma el sobre con el estado actual. Si hubo error, lo incluye. 
        if error:
            status_payload["error"] = error

        status_path = self.out_dir / f"status_{interview_id}.json"
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(status_payload, f, ensure_ascii=False, indent=2) # --> Escribe/actualiza un archivo Json con el estado. Formato legible.

        print(f"[Evaluator] Status: {status_payload}")  # --> Log a consola
