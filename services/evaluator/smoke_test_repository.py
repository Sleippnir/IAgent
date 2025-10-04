# services/evaluator/smoke_test_repository.py
import asyncio
from services.evaluator.app.infrastructure.repository import FileMockRepository

async def main():
    repo = FileMockRepository()
    ctx = await repo.get_interview_context("demo-001")
    print("CTX keys:", list(ctx.keys()))  # NICO --> Deberías ver: interview_id, system_prompt, rubric, jd, full_transcript

if __name__ == "__main__":
    asyncio.run(main())
