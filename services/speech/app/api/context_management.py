from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
import logging
from ..services.context_system_service import ContextService as IntelligentContextService
# from ..services.redis_context_cache import get_redis_context_cache
from ..infrastructure.repositories.interview_repository import SupabaseInterviewRepository
# from ..services.context_service import ContextService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context", tags=["Context Management"])

# Dependencias
def get_context_services():
    interview_repo = SupabaseInterviewRepository()
    context_service = IntelligentContextService(interview_repo)
    return {
        'intelligent_context': context_service,
        # 'redis_cache': get_redis_context_cache(),
        'context_service': context_service
    }

@router.get("/health")
async def get_context_health(services: dict = Depends(get_context_services)):
    """
    Obtiene el estado de salud del sistema de contexto
    """
    try:
        # cache_health = await services['redis_cache'].get_cache_health()
        cache_health = {"redis_connected": False}  # Placeholder
        
        return {
            "status": "healthy",
            "cache_health": cache_health,
            "services_active": {
                "intelligent_context": True,
                "redis_cache": cache_health.get('redis_connected', False),
                "context_service": True
            }
        }
    except Exception as e:
        logger.error(f"Error checking context health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{interview_id}")
async def get_interview_context_stats(
    interview_id: str,
    services: dict = Depends(get_context_services)
):
    """
    Obtiene estadísticas de contexto para una entrevista específica
    """
    try:
        # Obtener estadísticas del cache
        # cache_stats = await services['redis_cache'].get_interview_stats(interview_id)
        cache_stats = {}  # Placeholder
        
        # Obtener contexto actual
        context_data = await services['intelligent_context'].get_context_data(interview_id)
        
        if not context_data:
            raise HTTPException(status_code=404, detail="Interview context not found")
        
        return {
            "interview_id": interview_id,
            "context_data": {
                "job_role": context_data.job_role,
                "candidate_name": context_data.candidate_name,
                "relevant_qa_count": len(context_data.relevant_qa),
                "avg_relevance_score": (
                    sum(qa.relevance_score for qa in context_data.relevant_qa) / len(context_data.relevant_qa)
                    if context_data.relevant_qa else 0
                )
            },
            "cache_stats": cache_stats or {},
            "timestamp": context_data.__dict__.get('created_at', 'N/A')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting context stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview/{interview_id}")
async def preview_context(
    interview_id: str,
    current_question: Optional[str] = None,
    services: dict = Depends(get_context_services)
):
    """
    Previsualiza el contexto que se enviará a la LLM
    """
    try:
        # Obtener contexto mejorado
        enhanced_context = await services['intelligent_context'].get_enhanced_context(
            interview_id, 
            current_question or ""
        )
        
        if not enhanced_context:
            raise HTTPException(status_code=404, detail="Context not found")
        
        # Obtener datos estructurados también
        context_data = await services['intelligent_context'].get_context_data(
            interview_id,
            current_question or ""
        )
        
        return {
            "interview_id": interview_id,
            "enhanced_context": enhanced_context,
            "structured_data": {
                "job_role": context_data.job_role if context_data else None,
                "candidate_name": context_data.candidate_name if context_data else None,
                "relevant_qa": [
                    {
                        "question": qa.question,
                        "answer": qa.answer[:200] + "..." if len(qa.answer) > 200 else qa.answer,
                        "relevance_score": qa.relevance_score
                    }
                    for qa in (context_data.relevant_qa if context_data else [])
                ]
            },
            "context_length": len(enhanced_context),
            "current_question": current_question
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh/{interview_id}")
async def refresh_context(
    interview_id: str,
    services: dict = Depends(get_context_services)
):
    """
    Fuerza la actualización del contexto para una entrevista
    """
    try:
        # Invalidar cache
        success = await services['intelligent_context'].invalidate_cache(
            interview_id=interview_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to invalidate cache")
        
        # Obtener nuevo contexto
        new_context = await services['intelligent_context'].get_context_data(interview_id)
        
        if not new_context:
            raise HTTPException(status_code=404, detail="Could not refresh context")
        
        return {
            "status": "refreshed",
            "interview_id": interview_id,
            "new_context": {
                "job_role": new_context.job_role,
                "candidate_name": new_context.candidate_name,
                "relevant_qa_count": len(new_context.relevant_qa)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/cleanup")
async def cleanup_cache(services: dict = Depends(get_context_services)):
    """
    Limpia el cache expirado
    """
    try:
        cleanup_result = await services['intelligent_context'].cleanup_cache()
        
        return {
            "status": "completed",
            "cleanup_result": cleanup_result
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qa/search")
async def search_qa(
    job_role: str,
    query: Optional[str] = None,
    limit: int = 10,
    services: dict = Depends(get_context_services)
):
    """
    Busca preguntas y respuestas relevantes para un rol específico
    """
    try:
        # Usar el servicio inteligente para buscar Q&A
        context_data = await services['intelligent_context'].get_context_data(
            "temp_search",  # ID temporal para búsqueda
            current_question=query or ""
        )
        
        if not context_data or not context_data.relevant_qa:
            return {
                "job_role": job_role,
                "query": query,
                "results": [],
                "total_found": 0
            }
        
        # Filtrar y limitar resultados
        results = [
            {
                "question": qa.question,
                "answer": qa.answer,
                "relevance_score": qa.relevance_score
            }
            for qa in context_data.relevant_qa[:limit]
        ]
        
        return {
            "job_role": job_role,
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching Q&A: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_context_metrics(services: dict = Depends(get_context_services)):
    """
    Obtiene métricas generales del sistema de contexto
    """
    try:
        # cache_health = await services['redis_cache'].get_cache_health()
        cache_health = {"redis_connected": False, "total_keys": 0}  # Placeholder
        
        return {
            "cache_metrics": cache_health,
            "system_status": {
                "intelligent_context_active": True,
                "redis_connected": cache_health.get('redis_connected', False),
                "total_cache_keys": cache_health.get('total_keys', 0)
            },
            "performance": {
                "qa_cache_keys": cache_health.get('qa_cache_keys', 0),
                "context_cache_keys": cache_health.get('context_cache_keys', 0),
                "stats_cache_keys": cache_health.get('stats_cache_keys', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting context metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/{interview_id}")
async def test_context_pipeline(
    interview_id: str,
    test_question: str,
    services: dict = Depends(get_context_services)
):
    """
    Prueba el pipeline completo de contexto con una pregunta de ejemplo
    """
    try:
        import time
        start_time = time.time()
        
        # Obtener contexto mejorado
        enhanced_context = await services['intelligent_context'].get_enhanced_context(
            interview_id,
            test_question
        )
        
        # Obtener datos estructurados
        context_data = await services['intelligent_context'].get_context_data(
            interview_id,
            test_question
        )
        
        processing_time = time.time() - start_time
        
        return {
            "test_results": {
                "interview_id": interview_id,
                "test_question": test_question,
                "processing_time_ms": round(processing_time * 1000, 2),
                "context_generated": enhanced_context is not None,
                "context_length": len(enhanced_context) if enhanced_context else 0,
                "relevant_qa_found": len(context_data.relevant_qa) if context_data else 0
            },
            "context_preview": enhanced_context[:500] + "..." if enhanced_context and len(enhanced_context) > 500 else enhanced_context,
            "relevant_qa_preview": [
                {
                    "question": qa.question[:100] + "..." if len(qa.question) > 100 else qa.question,
                    "relevance_score": qa.relevance_score
                }
                for qa in (context_data.relevant_qa[:3] if context_data else [])
            ]
        }
        
    except Exception as e:
        logger.error(f"Error testing context pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))