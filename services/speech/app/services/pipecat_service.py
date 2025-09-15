#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#
import os
import sys

from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.gemini_multimodal_live import GeminiMultimodalLiveLLMService
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport, FastAPIWebsocketParams
from ..database import get_db_connection
from ..repositories import SQLiteInterviewRepository

load_dotenv(override=True)

def load_base_prompt():
    with open("test_data/interviewer_prompt.md", "r") as f:
        return f.read()

BASE_SYSTEM_INSTRUCTION = load_base_prompt()


async def run_bot(websocket, session_id: str, role_id: str):
    logger.info(f"Starting bot for session: {session_id}, role: {role_id}")

    db_connection = get_db_connection()
    repo = SQLiteInterviewRepository(db_connection)

    role = repo.get_role_by_id(role_id)
    questions = repo.get_questions_by_role_id(role_id)
    db_connection.close()

    if not role or not questions:
        logger.error(f"Could not find role or questions for role_id: {role_id}")
        return

    # Dynamically construct the system prompt
    dynamic_system_prompt = f"""
{BASE_SYSTEM_INSTRUCTION}

### Job Description
{role['jd_text']}
"""

    # Dynamically construct the initial context
    initial_context = [
        {"role": "system", "content": dynamic_system_prompt},
        {"role": "user", "content": f"Hello! I am ready to begin the interview for the {role['title']} position."},
        {"role": "assistant", "content": f"Great. The first question is: {questions[0]['question_text']}"}
    ]

    pipecat_transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    llm = GeminiMultimodalLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        voice_id="Kore",
        transcribe_user_audio=True,
        transcribe_model_audio=True,
    )

    context = OpenAILLMContext(initial_context)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            pipecat_transport.input(),
            context_aggregator.user(),
            llm,  # LLM
            pipecat_transport.output(),
            context_aggregator.assistant(),
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
        logger.info("Pipecat Client connected")
        # Kick off the conversation.
        await task.queue_frames([LLMRunFrame()])

    @pipecat_transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Pipecat Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)
