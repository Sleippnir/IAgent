from typing import Optional, Dict, Any
from supabase import create_client, Client
import os
import logging


class SupabaseInterviewRepository:
    """Implementación del repositorio de entrevistas usando Supabase."""
    
    def __init__(self, silent: bool = True):
        """Inicializa el repositorio con la configuración de Supabase.
        
        Args:
            silent: Si es True, no lanza excepción por variables faltantes
        """
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Client] = None
        
        if not self.supabase_url or not self.supabase_key:
            if not silent:
                raise ValueError("SUPABASE_URL y SUPABASE_ANON_KEY deben estar configuradas")
            return
            
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            if not silent:
                raise e
    
    async def get_interview_context(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el contexto de una entrevista desde Supabase.
        
        Args:
            interview_id: ID de la entrevista
            
        Returns:
            Diccionario con información de la entrevista o None si no se encuentra
            
        Raises:
            Exception: Si hay un error en la consulta a la base de datos
        """
        try:
            # Consulta con joins incluyendo prompts usando PostgREST
            result = self.client.table("interviews").select(
                "id_interview, is_active, is_complete, candidates(name), jobs(job_role, description), prompts(prompt_type, content)"
            ).eq("id_interview", interview_id).execute()
            
            if result.data and len(result.data) > 0:
                interview_data = result.data[0]
                
                # Validar que los datos anidados existan
                if not interview_data.get('candidates'):
                    logging.warning(f"No se encontró información del candidato para interview_id: {interview_id}")
                    return None
                    
                if not interview_data.get('jobs'):
                    logging.warning(f"No se encontró información del trabajo para interview_id: {interview_id}")
                    return None
                
                candidate_data = interview_data['candidates']
                job_data = interview_data['jobs']
                
                # Obtener información del prompt si existe
                prompt_data = interview_data.get('prompts')
                custom_prompt = None
                if prompt_data and prompt_data.get('content'):
                    custom_prompt = prompt_data['content']
                
                return {
                    'job_role': job_data.get('job_role', 'Unknown Position'),
                    'job_description': job_data.get('description'),
                    'candidate_name': candidate_data.get('name', 'Unknown Candidate'),
                    'interview_status': 'active' if interview_data.get('is_active') else 'inactive',
                    'is_complete': interview_data.get('is_complete', False),
                    'custom_prompt': custom_prompt,
                    'prompt_type': prompt_data.get('prompt_type') if prompt_data else None
                }
            
            logging.info(f"No se encontró entrevista con ID: {interview_id}")
            return None
            
        except Exception as e:
            logging.error(f"Error al consultar información de entrevista {interview_id}: {str(e)}")
            raise Exception(f"Error fetching interview context: {e}")