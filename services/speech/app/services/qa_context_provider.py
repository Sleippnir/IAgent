from typing import List, Optional
import logging
import os
from dataclasses import dataclass

from ..infrastructure.repositories.questions_repository import QuestionsRepository, QAItem


logger = logging.getLogger(__name__)

@dataclass
class ContextData:
    """Simplified context data structure"""
    job_role: str
    technical_qa: List[QAItem]
    general_qa: List[QAItem]
    total_items: int

class QAContextProvider:
    """Agregador de contexto simplificado que obtiene Q&A por job_role."""
    
    def __init__(self, questions_repository: QuestionsRepository):
        """Inicializa el agregador de contexto simplificado.
        
        Args:
            questions_repository: Repositorio de preguntas
        """
        self._questions_repository = questions_repository
        # Configuración desde variables de entorno
        self._max_technical_qa = int(os.getenv('MAX_TECHNICAL_QUESTIONS', '10'))
        self._max_general_qa = int(os.getenv('MAX_GENERAL_QUESTIONS', '5'))
        self._max_total_qa = self._max_technical_qa + self._max_general_qa
    
    async def aggregate_context_for_job(self, job_role: str) -> ContextData:
        """Agrega contexto para un rol de trabajo específico.
        
        Args:
            job_role: Rol del trabajo para filtrar preguntas técnicas
            
        Returns:
            ContextData con preguntas técnicas y generales limitadas
        """
        try:
            # Obtener Q&A por job_role con límite total
            qa_items = await self._questions_repository.get_qa_by_job_role(job_role, self._max_total_qa)
            
            # Separar por tipo y aplicar límites específicos
            all_technical = [item for item in qa_items if item.source == 'technical']
            all_general = [item for item in qa_items if item.source == 'general']
            
            # Limitar preguntas técnicas y generales
            technical_qa = all_technical[:self._max_technical_qa]
            general_qa = all_general[:self._max_general_qa]
            
            context_data = ContextData(
                job_role=job_role,
                technical_qa=technical_qa,
                general_qa=general_qa,
                total_items=len(technical_qa) + len(general_qa)
            )
            
            logger.debug(f"Contexto agregado para {job_role}: {len(technical_qa)}/{self._max_technical_qa} técnicas, {len(general_qa)}/{self._max_general_qa} generales")
            return context_data
            
        except Exception as e:
            logger.error(f"Error agregando contexto para {job_role}: {str(e)}")
            return ContextData(
                job_role=job_role,
                technical_qa=[],
                general_qa=[],
                total_items=0
            )
    
    def format_context_for_injection(self, context_data: ContextData) -> str:
        """Formatea el contexto para inyección en el prompt.
        
        Args:
            context_data: Datos de contexto a formatear
            
        Returns:
            Contexto formateado como string
        """
        if context_data.total_items == 0:
            logger.info("No hay preguntas disponibles para el contexto")
            return ""
        
        logger.info(f"Formateando contexto para {context_data.job_role}: {context_data.total_items} preguntas totales")
        
        context_parts = [f"\n=== CONOCIMIENTO PARA {context_data.job_role.upper()} ==="]
        
        # Agregar preguntas técnicas
        if context_data.technical_qa:
            logger.info(f"Agregando {len(context_data.technical_qa)} preguntas técnicas")
            context_parts.append("\n--- PREGUNTAS TÉCNICAS ---")
            for i, item in enumerate(context_data.technical_qa, 1):
                logger.debug(f"Pregunta técnica {i}: {item.question[:100]}...")
                context_parts.append(f"\n{i}. PREGUNTA: {item.question}")
                context_parts.append(f"   RESPUESTA: {item.answer}")
        
        # Agregar preguntas generales
        if context_data.general_qa:
            logger.info(f"Agregando {len(context_data.general_qa)} preguntas generales")
            context_parts.append("\n--- PREGUNTAS GENERALES ---")
            for i, item in enumerate(context_data.general_qa, 1):
                logger.debug(f"Pregunta general {i}: {item.question[:100]}...")
                context_parts.append(f"\n{i}. PREGUNTA: {item.question}")
                context_parts.append(f"   RESPUESTA: {item.answer}")
        
        context_parts.append("\n=== FIN CONOCIMIENTO ===\n")
        
        formatted_context = "\n".join(context_parts)
        logger.info(f"Contexto formateado: {len(formatted_context)} caracteres")
        
        return formatted_context