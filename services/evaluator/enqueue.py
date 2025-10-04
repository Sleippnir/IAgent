# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/enqueue.py
# Productor simple: encola un job con {"interview_id": "<UUID>"} en el stream de Redis.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

import argparse, json, os, asyncio
from redis.asyncio import Redis

STREAM_NAME = os.getenv("EVALUATOR_STREAM", "evaluation_jobs") # --> Stream/cola
REDIS_URI   = os.getenv("REDIS_URI", "redis://redis:6379/0") # --> Conexión Redis

async def main(interview_id: str):
    r = Redis.from_url(REDIS_URI) # --> Cliente Redis
    payload = {"interview_id": interview_id}  # --> Cuerpo del job
    await r.xadd(STREAM_NAME, {"payload": json.dumps(payload)}) # --> Encolamos como campo "payload"
    print(f"[Enqueue] Job encolado: stream={STREAM_NAME} interview_id={interview_id}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True, help="id_interview real")
    args = p.parse_args()
    asyncio.run(main(args.id))
