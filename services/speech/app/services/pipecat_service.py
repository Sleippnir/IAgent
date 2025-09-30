#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
import os
from ..infrastructure.repositories.interview_repository import SupabaseInterviewRepository
from .context_system_service import ContextService
from ..infrastructure.repositories.questions_repository import QuestionsRepository
from .qa_context_provider import QAContextProvider

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.gemini_multimodal_live import GeminiMultimodalLiveLLMService
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

load_dotenv(override=True)

# La instrucción del sistema ahora se maneja en ContextService

# Instancias globales de servicios
_interview_repository = None
_context_service = None
_qa_service = None

def get_context_service():
    """Obtiene la instancia del servicio de contexto."""
    global _interview_repository, _context_service
    
    if _context_service is None:
        _interview_repository = SupabaseInterviewRepository()
        _context_service = ContextService(_interview_repository)
    
    return _context_service

def get_qa_service():
    """Obtiene la instancia del servicio de Q&A."""
    global _qa_service
    
    if _qa_service is None:
        _qa_service = QuestionsRepository()
    
    return _qa_service


async def run_bot(webrtc_connection, interview_id: str = None):
    try:
        print(f"🚀 INICIANDO RUN_BOT para interview_id: {interview_id}", flush=True)

        # Obtener servicios
        context_service = get_context_service()
        qa_service = get_qa_service()
        
        # Obtener contexto dinámico basado en interview_id usando el servicio
        system_instruction = await context_service.get_dynamic_context(interview_id)
        
        # Obtener información de la entrevista para extraer job_role
        interview_repository = context_service.interview_repository
        interview_context = await interview_repository.get_interview_context(interview_id)
        
        # Extraer job_role del contexto de la entrevista
        job_role = None
        logger.info(f"Contexto de entrevista recibido: {interview_context}")
        if interview_context:
            job_role = interview_context.get('job_role')
            logger.info(f"Job role extraído: {job_role}")
        else:
            logger.warning("No se pudo extraer job_role del contexto de entrevista")
        
        # Obtener Q&A relevantes si tenemos job_role
        qa_context = ""
        if job_role:
            logger.info(f"Iniciando agregación de contexto para job_role: {job_role}")
            context_aggregator = QAContextProvider(
                questions_repository=qa_service
            )
            context_data = await context_aggregator.aggregate_context_for_job(job_role)
            qa_context = context_aggregator.format_context_for_injection(context_data)
            logger.info(f"Contexto Q&A obtenido para job_role: {job_role}")
        
        # Combinar system_instruction con contexto Q&A
        if qa_context:
            enhanced_system_instruction = f"{system_instruction}\n\n### Relevant Q&A Context\n{qa_context}"
        else:
            enhanced_system_instruction = system_instruction
        
        logger.info(f"Iniciando bot para entrevista {interview_id} con servicios Q&A integrados")
        
        # Configurar VAD con parámetros optimizados para conexión rápida
        vad_params = VADParams(
            confidence=0.6,  # Reducido para detección más rápida
            start_secs=0.1,  # Reducido para respuesta más rápida
            stop_secs=0.15,  # Optimizado para análisis rápido
            min_volume=0.5,  # Reducido para mayor sensibilidad
        )
        
        # Crear el analizador VAD
        vad_analyzer = SileroVADAnalyzer(params=vad_params)
        
        # Crear el Turn Analyzer
        turn_analyzer = LocalSmartTurnAnalyzerV3()
        
        pipecat_transport = SmallWebRTCTransport(
            webrtc_connection=webrtc_connection,
            params=TransportParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad_analyzer,          # VAD configurado
                turn_analyzer=turn_analyzer,        # Turn Analyzer agregado
                audio_out_10ms_chunks=1,            # Reducido para menor latencia
                audio_in_sample_rate=16000,         # Optimizado para procesamiento rápido
                audio_out_sample_rate=16000,        # Consistente con entrada
            ),
        )

        llm = GeminiMultimodalLiveLLMService(
            api_key=os.getenv("GOOGLE_API_KEY"),
            voice_id="Kore",  # Aoede, Charon, Fenrir, Kore, Puck
            transcribe_user_audio=True,
            transcribe_model_audio=True,
            system_instruction=enhanced_system_instruction,
        )

        # Crear contexto inicial con system instruction mejorado
        initial_context = OpenAILLMContext(
            [
                {
                    "role": "system",
                    "content": enhanced_system_instruction,
                },
                {
                    "role": "user",
                    "content": "Start by greeting the user warmly and introducing yourself.",
                }
            ],
        )

        # Crear context aggregator desde el LLM con el contexto inicial
        context_aggregator = llm.create_context_aggregator(initial_context)

        pipeline = Pipeline(
            [
                pipecat_transport.input(),
                context_aggregator.user(),
                llm,  # LLM
                context_aggregator.assistant(),
                pipecat_transport.output(),
            ]
        )

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        @pipecat_transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            logger.info(f"Pipecat Client connected para entrevista {interview_id}")
            
            # Kick off the conversation.
            await task.queue_frames([LLMRunFrame()])

        @pipecat_transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            logger.info(f"Pipecat Client disconnected para entrevista {interview_id}")
            
            await task.cancel()

        runner = PipelineRunner(handle_sigint=False)

        await runner.run(task)
    
    except Exception as e:
        logger.error(f"❌ Error en run_bot para interview_id {interview_id}: {str(e)}")
        logger.exception("Detalles del error:")
        raise