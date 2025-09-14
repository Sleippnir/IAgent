import json
from typing import List, Optional, Dict
import redis.asyncio as redis

from ...domain.entities.session import Session, Question, Turn, QuestionSummary, PinnedContext
from ...domain.repositories.session_repository import SessionRepository

class RedisSessionRepository(SessionRepository):
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client

    async def get_session(self, session_id: str) -> Optional[Session]:
        session_data = await self._redis.get(f"session:{session_id}")
        if session_data:
            return Session.parse_raw(session_data)
        return None

    async def save_session(self, session: Session) -> None:
        await self._redis.set(f"session:{session.session_id}", session.json())

    async def get_questions(self, role_id: str) -> List[Question]:
        questions_data = await self._redis.get(f"questions:{role_id}")
        if questions_data:
            return [Question.parse_raw(q) for q in json.loads(questions_data)]
        return []

    async def save_questions(self, role_id: str, questions: List[Question]) -> None:
        questions_data = json.dumps([q.json() for q in questions])
        await self._redis.set(f"questions:{role_id}", questions_data)

    async def get_transcript_turns(self, session_id: str, question_id: str) -> List[Turn]:
        turns_data = await self._redis.lrange(f"transcript:{session_id}:{question_id}", 0, -1)
        return [Turn.parse_raw(t) for t in turns_data]

    async def add_transcript_turn(self, session_id: str, question_id: str, turn: Turn) -> None:
        await self._redis.rpush(f"transcript:{session_id}:{question_id}", turn.json())

    async def clear_transcript(self, session_id: str, question_id: str) -> None:
        await self._redis.delete(f"transcript:{session_id}:{question_id}")

    async def get_all_transcripts_for_session(self, session_id: str) -> Dict[str, List[Turn]]:
        # This is a bit more complex with Redis and might require scanning keys.
        # For now, we'll leave it unimplemented as it's not critical for the main flow.
        raise NotImplementedError

    async def archive_transcript(self, session_id: str, question_id: str, turns: List[Turn]) -> None:
        turns_data = json.dumps([t.json() for t in turns])
        await self._redis.set(f"archive:{session_id}:{question_id}", turns_data)

    async def get_archived_transcript(self, session_id: str, question_id: str) -> List[Turn]:
        turns_data = await self._redis.get(f"archive:{session_id}:{question_id}")
        if turns_data:
            return [Turn.parse_raw(t) for t in json.loads(turns_data)]
        return []

    async def get_summaries(self, session_id: str) -> List[QuestionSummary]:
        summaries_data = await self._redis.lrange(f"summaries:{session_id}", 0, -1)
        return [QuestionSummary.parse_raw(s) for s in summaries_data]

    async def add_summary(self, session_id: str, summary: QuestionSummary) -> None:
        await self._redis.rpush(f"summaries:{session_id}", summary.json())

    async def get_pinned_context(self, session_id: str) -> Optional[PinnedContext]:
        context_data = await self._redis.get(f"pinned_context:{session_id}")
        if context_data:
            return PinnedContext.parse_raw(context_data)
        return None

    async def save_pinned_context(self, session_id: str, context: PinnedContext) -> None:
        await self._redis.set(f"pinned_context:{session_id}", context.json())
