# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/app/infrastructure/llm_provider.py
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
from ..domain.entities.interview import Interview # --> Entidad fuerte con from_dict/to_dict
from .config import Settings # --> Config (pydantic BaseSettings)
from .persistence.supabase.interview_repository import load_interview_from_supabase # --> función async que trae Interview desde DB
# NICO --> Std libs
import json
import os # --> Carga .env de la raíz y configura flags/modelos por defecto.
import asyncio
from pathlib import Path
# --- Helpers OpenAI/Gemini
from openai import OpenAI # --> SDK OpenAI (chat.completions)
import google.generativeai as genai # --> SDK Gemini (generate_content)
# --- .env
try:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv(usecwd=True))  # --> busca .env desde CWD (C:\IAgent-stable)
except Exception as e:
    print(f"[WARN] .env no cargado automáticamente: {e}")

# ================================
# Settings / Flags / Defaults
# ================================
# Initialize settings
settings = Settings()
# --> Flags de activación por .env (1=on, 0=off)
ENABLE_OPENAI     = os.getenv("EVALUATOR_ENABLE_OPENAI", "1") == "1"
ENABLE_GEMINI     = os.getenv("EVALUATOR_ENABLE_GEMINI", "1") == "1"
ENABLE_OPENROUTER = os.getenv("EVALUATOR_ENABLE_OPENROUTER", "0") == "1"

# --> Modelos por defecto (coherentes con lo que ya probaste)
DEFAULT_OPENAI_MODEL  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_GEMINI_MODEL  = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # <-- validado en tu ping

# --> Límite y temperatura (ajustables por .env)
OPENAI_MAX_TOKENS     = int(os.getenv("OPENAI_MAX_TOKENS", "512"))
OPENAI_TEMPERATURE    = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

OPENROUTER_MAX_TOKENS  = int(os.getenv("OPENROUTER_MAX_TOKENS", "512"))
OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", "0.2"))

# --> Claves
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY      = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY")

# ================================
# Helpers de inicialización
# ================================
_openai_client = None
_gemini_ready  = False

def _get_openai_client():
    # --> Lazy init del cliente OpenAI sólo si hay key.
    global _openai_client
    if OPENAI_API_KEY and _openai_client is None:
        try:
            _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            print(f"[WARN] OpenAI init error: {e}")
            _openai_client = None
    return _openai_client

def _setup_gemini():
    # --> Configura google-generativeai una única vez.
    global _gemini_ready
    if GOOGLE_API_KEY and not _gemini_ready:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            _gemini_ready = True
        except Exception as e:
            print(f"[WARN] Gemini configure error: {e}")
            _gemini_ready = False
    return _gemini_ready



# --- Step 1: Data Loading Function ---
# --------------------------------------------------------------------
# --> Step 1: Data Loading Function
# Carga una Interview desde: archivo local ('file'), Supabase ('supabase') o alias 'db' (redirige a 'supabase').
# --------------------------------------------------------------------
def load_interview_from_source(source_type: str, identifier: str) -> Interview:
    """
    Instantiates and populates an Interview object from a given data source.

    Args:
        source_type (str): The type of the data source. Can be 'file', 'supabase', or 'db'.
        identifier (str): The file path (for 'file') or a record ID (for 'supabase'/'db').

    Returns:
        Interview: A populated instance of the Interview class.
        
    Raises:
        ValueError: If the source_type is not supported.
        FileNotFoundError: If the file is not found for source_type 'file'.
    """
    print(f"Loading interview from {source_type} using identifier: {identifier}") # --> Log: qué y desde dónde
    
    # --------------------------
    # MODO 'file' (JSON local)
    # --------------------------
    if source_type == 'file':
        try:
            # Try multiple locations for the file
            # --> Buscamos el archivo en varias ubicaciones razonables
            possible_paths = [
                identifier,  # Original path # --> Ruta pasada tal cual
                f"examples/{identifier}",  # Check examples folder # --> Carpeta de ejemplos
                f"storage/{identifier}",  # Check storage folder # --> Carpeta de storage
            ]
            
            file_found = False
            for path in possible_paths:
                try:
                    with open(path, 'r') as f: # --> Intenta abrir cada ruta
                        data = json.load(f) # --> Parseo JSON -> dict
                        file_found = True
                        print(f"Successfully loaded file from: {path}")
                        break
                except FileNotFoundError:
                    continue # --> Probar siguiente path
            
            if not file_found:
                # --> Error claro con todas las rutas probadas
                raise FileNotFoundError(f"File not found at any of these locations: {possible_paths}")
            
            # --> Transforma dict -> Interview mediante la entidad
            return Interview.from_dict(data)
        except FileNotFoundError:
            print(f"Error: File not found at {identifier}") # --> Log de error
            raise
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {identifier}") # --> Log de error de parseo
            raise

    # --------------------------
    # MODO 'supabase' (DB real)
    # --------------------------        
    elif source_type == 'supabase':
        # Use asyncio to run the async function
        # --> Esta rama usa una función async; acá la corrés con loop sync
        try:
            loop = asyncio.get_event_loop() # --> Obtiene loop actual
        except RuntimeError:
            loop = asyncio.new_event_loop() # --> Crea loop si no hay
            asyncio.set_event_loop(loop)
        
        interview = loop.run_until_complete(load_interview_from_supabase(identifier)) # --> Await bloqueante
        if interview:
            return interview # --> Ya viene como Interview
        else:
            raise ValueError(f"No interview found in Supabase with ID: {identifier}")
    
    # --------------------------
    # MODO 'db' (alias legacy)
    # --------------------------       
    elif source_type == 'db':
        # Legacy support - redirect to supabase
        print("'db' source type is deprecated, using 'supabase' instead.") # --> Aviso de alias legacy
        return load_interview_from_source('supabase', identifier) # --> Redirige a supabase
        
    # --------------------------
    # MODO no soportado
    # --------------------------    
    else:
        raise ValueError(f"Unsupported source type: '{source_type}'. Use 'file', 'supabase', or 'db'.")

# --- Step 2: Evaluation Function ---

# --------------------------------------------------------------------
# --> Step 2: Evaluation Functions (llamadas a LLMs)
# Requiere: OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY en entorno.
# --------------------------------------------------------------------

# --- Actual LLM API call implementations ---
# NOTE: Ensure you have set the following environment variables:
# OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY

async def call_openai_gpt5(prompt, rubric, transcript):
    """
    Llama a OpenAI con el modelo configurado (por .env o default).
    Usa chat.completions del SDK 2.x; parámetros seguros.
    """
    if not ENABLE_OPENAI:
        return "[OpenAI disabled by env]"
    print(f"Calling OpenAI API ({DEFAULT_OPENAI_MODEL})...")
    try:
        client = _get_openai_client()
        if not client:
            raise RuntimeError("Cliente OpenAI no inicializado (¿falta OPENAI_API_KEY?).")

        full_prompt = (
            f"System Prompt: {prompt}\n\n"
            f"Evaluation Rubric:\n{rubric}\n\n"
            f"Interview Transcript:\n{transcript}\n\n"
            f"---\nPlease provide your evaluation."
        )

        resp = client.chat.completions.create(
            model=DEFAULT_OPENAI_MODEL,  # --> gpt-4o-mini por .env
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "512")),    # --> límite seguro
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")) # --> determinista-ish
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        msg = f"Error calling OpenAI API: {e}"
        print(msg)
        return msg


async def call_google_gemini(prompt, rubric, transcript):
    """
    Llama a Gemini con el alias que tu cuenta expone (gemini-2.5-flash por defecto).
    """
    if not ENABLE_GEMINI:
        return "[Gemini disabled by env]"
    print(f"Calling Google Gemini API ({DEFAULT_GEMINI_MODEL})...")
    try:
        if not _setup_gemini():
            raise RuntimeError("Gemini no inicializado (¿falta GOOGLE_API_KEY?).")

        model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
        full_prompt = (
            f"System Prompt: {prompt}\n\n"
            f"Evaluation Rubric:\n{rubric}\n\n"
            f"Interview Transcript:\n{transcript}\n\n"
            f"---\nPlease provide your evaluation."
        )
        resp = model.generate_content(full_prompt)

        # --> extracción defensiva del texto
        txt = getattr(resp, "text", None)
        if not txt and getattr(resp, "candidates", None):
            parts = resp.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                txt = parts[0].text
        return (txt or "").strip()
    except Exception as e:
        msg = f"Error calling Google Gemini API: {e}"
        print(msg)
        return msg


async def call_openrouter_deepseek(prompt, rubric, transcript):
    """
    Llama a DeepSeek vía OpenRouter si está habilitado y hay API key.
    """
    if not ENABLE_OPENROUTER:
        return "[OpenRouter disabled by env]"
    print(f"Calling OpenRouter API ({settings.DEEPSEEK_MODEL})...")
    try:
        api_key = OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY no seteada.")

        client = OpenAI(
            base_url=getattr(settings, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=api_key,
        )
        full_prompt = (
            f"System Prompt: {prompt}\n\n"
            f"Evaluation Rubric:\n{rubric}\n\n"
            f"Interview Transcript:\n{transcript}\n\n"
            f"---\nPlease provide your evaluation."
        )
        resp = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=int(os.getenv("OPENROUTER_MAX_TOKENS", "512")),
            temperature=float(os.getenv("OPENROUTER_TEMPERATURE", "0.2")),
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        msg = f"Error calling OpenRouter API: {e}"
        print(msg)
        return msg



# --------------------------------------------------------------------
# --> Orquestador de evaluaciones: llena evaluation_1/2/3 en Interview
# --------------------------------------------------------------------
async def run_evaluations(interview: Interview) -> Interview:
    """
    Llama a los LLMs habilitados y llena evaluation_1/2/3.
    Si un proveedor está deshabilitado o falla, deja un texto explicativo (no rompe el flujo).
    """
    print(f"\nRunning evaluations for interview ID: {interview.interview_id}")

    # OpenAI
    try:
        interview.evaluation_1 = await call_openai_gpt5(
            interview.system_prompt, interview.rubric, interview.full_transcript
        )
    except Exception as e:
        interview.evaluation_1 = f"[OpenAI error] {e}"

    # Gemini
    try:
        interview.evaluation_2 = await call_google_gemini(
            interview.system_prompt, interview.rubric, interview.full_transcript
        )
    except Exception as e:
        interview.evaluation_2 = f"[Gemini error] {e}"

    # OpenRouter (opcional)
    try:
        interview.evaluation_3 = await call_openrouter_deepseek(
            interview.system_prompt, interview.rubric, interview.full_transcript
        )
    except Exception as e:
        interview.evaluation_3 = f"[OpenRouter error] {e}"

    print("Evaluations completed.")
    return interview


# --> Bloque ejecutable para "python -m ... --ping"
if __name__ == "__main__":
    import json, os
    from pathlib import Path
    try:
        # --> Carga .env desde la raíz del repo (C:\IAgent-stable\.env)
        from dotenv import find_dotenv, load_dotenv
        load_dotenv(find_dotenv(usecwd=True))
    except Exception as e:
        print(f"[WARN] .env no cargado: {e}")

    out = {}

    # ---- OpenAI ----
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # NICO --> usa tu key del .env
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # NICO --> si falla, probá "gpt-4.1-mini"
            messages=[{"role":"user","content":"Escribe: pong OpenAI"}],
            max_tokens=16,
            temperature=0
        )
        out["openai"] = {"ok": True, "reply": resp.choices[0].message.content.strip()}
    except Exception as e:
        out["openai"] = {"ok": False, "error": str(e)}

    # ---- Gemini ----
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")  # --> alternativas: "gemini-1.5-flash-8b", "gemini-pro"
        resp = model.generate_content("Responde exactamente: pong Gemini")
        txt = getattr(resp, "text", None) or (resp.candidates and resp.candidates[0].content.parts[0].text)
        out["gemini"] = {"ok": True, "reply": (txt or "").strip()}
    except Exception as e:
        out["gemini"] = {"ok": False, "error": str(e)}

    print(json.dumps(out, ensure_ascii=False, indent=2))

