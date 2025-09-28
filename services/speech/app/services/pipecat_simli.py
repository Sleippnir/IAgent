#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
import os
from ..infrastructure.repositories.interview_repository import SupabaseInterviewRepository
from .context_system_service import ContextService
from ..infrastructure.repositories.questions_repository import QuestionsRepository
from .qa_context_provider import QAContextProvider

import os

from dotenv import load_dotenv
from loguru import logger
from simli import SimliConfig

from pipecat.services.google.stt import GoogleSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService  
from pipecat.services.google.llm import GoogleLLMService
from pipecat.services.google.stt import Language
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.simli.video import SimliVideoService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams
from pipecat.frames.frames import EndTaskFrame, TTSSpeakFrame
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import FunctionCallParams
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.adapters.schemas.function_schema import FunctionSchema


load_dotenv(override=True)

_interview_repository = None
_context_service = None
_qa_service = None
# We store functions so objects (e.g. SileroVADAnalyzer) don't get
# instantiated. The function will be called when the desired transport gets
# selected.
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

async def end_conversation(params: FunctionCallParams):
    # Optional: speak a goodbye
    await params.llm.push_frame(TTSSpeakFrame("Okay, ending the session now."))
    # Push an EndTaskFrame upstream to terminate gracefully
    await params.llm.push_frame(EndTaskFrame(), FrameDirection.UPSTREAM)
    # Return a result object for the LLM (optional)
    await params.result_callback({"status": "ended"})

end_fn_schema = FunctionSchema(
    name="end_conversation",
    description="End the current session and say goodbye",
    properties={},
    required=[]
)

tools = ToolsSchema(standard_tools=[end_fn_schema])
# Register the tool with your LLM service


transport_params = {
    "daily": lambda: DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        video_out_enabled=True,
        video_out_is_live=True,
        video_out_width=512,
        video_out_height=512,
        vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
        turn_analyzer=LocalSmartTurnAnalyzerV3(params=SmartTurnParams()),
    ),
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        video_out_enabled=True,
        video_out_is_live=True,
        video_out_width=512,
        video_out_height=512,
        vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
        turn_analyzer=LocalSmartTurnAnalyzerV3(params=SmartTurnParams()),
    ),
}


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info(f"Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY")
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID", ""),
    )

    simli_ai = SimliVideoService(
        SimliConfig(os.getenv("SIMLI_API_KEY"), os.getenv("SIMLI_FACE_ID")),
    )

    llm = GoogleLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.5-flash",
    )
    
    llm.register_function(
        "end_conversation",
        end_conversation,
        cancel_on_interruption=True,
    )


    messages = [
        {
            "role": "system",
            "content": (
                "You are Kathia Slazar an AI agent performing structured job interviews over a WebRTC call. The current candidate (Marco Pantalone)is applying for a program manager position at the company Anyone AI. "
                "You have access to a tool called `end_conversation` "
                "When the user says goodbye or asks to end, you MUST call this tool using the function calling interface, not by describing it in text."
            ),
        },
    ]

    context = LLMContext(messages, tools=tools)
    context_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            context_aggregator.user(),
            llm,
            tts,
            simli_ai,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Client connected")
        # Start conversation - empty prompt to let LLM follow system instructions
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point compatible with Pipecat Cloud."""
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()