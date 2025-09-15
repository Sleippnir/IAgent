import asyncio
from fastapi import FastAPI, WebSocket
from loguru import logger

from app.services.pipecat_service import run_bot
from app.services.pipecat_service import run_bot
from app.database import create_tables, load_mock_data, get_db_connection
from app.core_client import CoreServiceClient

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_tables()
    conn = get_db_connection()
    load_mock_data(conn)
    conn.close()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Client connected for session: {session_id}")

    core_client = CoreServiceClient()
    role_id = await core_client.get_role_for_session(session_id)
    if not role_id:
        logger.error(f"No role found for session: {session_id}")
        await websocket.close(code=4001)
        return

    try:
        await run_bot(websocket, session_id, role_id)
    except Exception as e:
        logger.error(f"Error during bot execution: {e}")
    finally:
        logger.info(f"Client disconnected for session: {session_id}")