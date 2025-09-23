#!/usr/bin/env python3
"""
Repositorio de Preguntas - Acceso a datos de preguntas técnicas y generales

Este módulo maneja el acceso a las preguntas técnicas y generales almacenadas
en la base de datos, incluyendo la relación con jobs específicos.
"""

import os
import logging
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..database.supabase_connection import get_supabase_client

logger = logging.getLogger(__name__)

@dataclass
class QAItem:
    """Representa un elemento de pregunta y respuesta."""
    question: str
    answer: str
    source: str  # 'general' o 'technical'
    id: int

class QuestionsRepository:
    """
    Repositorio consolidado para acceder a preguntas técnicas y generales
    Incluye funcionalidades de Q&A con formato QAItem y Dict[str, Any]
    """
    
    def __init__(self):
        self.client = get_supabase_client(silent_env_error=True)

    async def get_qa_by_job_role(self, job_role: str, limit: int = None) -> List[QAItem]:
        """Obtiene preguntas técnicas y generales aleatorias para un rol específico en formato QAItem
        
        Args:
            job_role: Rol del trabajo para filtrar preguntas técnicas
            limit: Límite total de preguntas (se ignora, se usan límites específicos por tipo)
            
        Returns:
            Lista de QAItem con preguntas técnicas y generales aleatorias
        """
        try:
            qa_items = []
            
            # Obtener preguntas técnicas específicas del job (aleatorias)
            job_response = self.client.table("jobs") \
                .select("id_job") \
                .eq("job_role", job_role) \
                .limit(1) \
                .execute()
            
            if job_response.data:
                job_id = job_response.data[0]["id_job"]
                
                # Obtener límite de preguntas técnicas desde variables de entorno
                max_technical = int(os.getenv('MAX_TECHNICAL_QUESTIONS', '10'))
                
                # Obtener preguntas técnicas aleatorias para este job
                # Intentar usar función RPC, si falla usar consulta directa
                try:
                    technical_response = self.client.rpc(
                        'get_random_technical_questions_by_job',
                        {'job_id_param': job_id, 'limit_param': max_technical}
                    ).execute()
                    
                    # Si la función RPC no devuelve datos, usar consulta directa
                    if not technical_response.data:
                        raise Exception("RPC function returned no data")
                        
                except Exception as rpc_error:
                    # Usar consulta directa con JOIN y aleatorización mediante offset aleatorio
                    
                    # Primero obtener el total de preguntas para este job
                    count_response = self.client.table("technical_questions_answers_jobs") \
                        .select("*", count="exact") \
                        .eq("id_job", job_id) \
                        .execute()
                    
                    total_questions = count_response.count if count_response.count else 0
                    
                    if total_questions > 0:
                        # Generar offset aleatorio
                        max_offset = max(0, total_questions - max_technical)
                        random_offset = random.randint(0, max_offset) if max_offset > 0 else 0
                        
                        technical_response = self.client.table("technical_questions_answers_jobs") \
                            .select("id_tech_question_answer, technical_questions_answers(question, answer)") \
                            .eq("id_job", job_id) \
                            .range(random_offset, random_offset + max_technical - 1) \
                            .execute()
                    else:
                        technical_response = self.client.table("technical_questions_answers_jobs") \
                            .select("id_tech_question_answer, technical_questions_answers(question, answer)") \
                            .eq("id_job", job_id) \
                            .limit(max_technical) \
                            .execute()
                
                for row in technical_response.data:
                    tech_qa = row.get('technical_questions_answers', {})
                    question = tech_qa.get('question', '') if tech_qa else ''
                    answer = tech_qa.get('answer', '') if tech_qa else ''
                    if question and answer:
                        qa_items.append(QAItem(
                            id=row['id_tech_question_answer'],
                            question=question,
                            answer=answer,
                            source='technical'
                        ))
            
            # Obtener límite de preguntas generales desde variables de entorno
            max_general = int(os.getenv('MAX_GENERAL_QUESTIONS', '5'))
            
            # Obtener preguntas generales con aleatorización mediante offset aleatorio
            # Primero obtener el total de preguntas generales
            general_count_response = self.client.table('general_questions_answers') \
                .select('*', count='exact') \
                .execute()
            
            total_general = general_count_response.count if general_count_response.count else 0
            
            if total_general > 0:
                # Generar offset aleatorio para preguntas generales
                max_general_offset = max(0, total_general - max_general)
                random_general_offset = random.randint(0, max_general_offset) if max_general_offset > 0 else 0
                
                general_response = self.client.table('general_questions_answers') \
                    .select('id_gral_question_answer, question, answer') \
                    .range(random_general_offset, random_general_offset + max_general - 1) \
                    .execute()
            else:
                general_response = self.client.table('general_questions_answers') \
                    .select('id_gral_question_answer, question, answer') \
                    .limit(max_general) \
                    .execute()
            
            for item in general_response.data:
                qa_items.append(QAItem(
                    id=item["id_gral_question_answer"],
                    question=item["question"],
                    answer=item["answer"],
                    source="general"
                ))
            
            logger.info(f"Obtenidas {len(qa_items)} preguntas Q&A aleatorias para job_role: {job_role} (técnicas: {len([q for q in qa_items if q.source == 'technical'])}, generales: {len([q for q in qa_items if q.source == 'general'])})")
            return qa_items
            
        except Exception as e:
            logger.error(f"Error al obtener Q&A aleatorias para job_role {job_role}: {str(e)}")
            return []


questions_repository = QuestionsRepository()