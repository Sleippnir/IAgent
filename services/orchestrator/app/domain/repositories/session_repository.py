from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from ..entities.session import Session, Question, Turn, QuestionSummary, PinnedContext

class SessionRepository(ABC):
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[Session]:
        pass

    @abstractmethod
    async def save_session(self, session: Session) -> None:
        pass

    @abstractmethod
    async def get_questions(self, role_id: str) -> List[Question]:
        pass

    @abstractmethod
    async def save_questions(self, role_id: str, questions: List[Question]) -> None:
        pass

    @abstractmethod
    async def get_transcript_turns(self, session_id: str, question_id: str) -> List[Turn]:
        pass

    @abstractmethod
    async def add_transcript_turn(self, session_id: str, question_id: str, turn: Turn) -> None:
        pass

    @abstractmethod
    async def clear_transcript(self, session_id: str, question_id: str) -> None:
        pass

    @abstractmethod
    async def get_all_transcripts_for_session(self, session_id: str) -> Dict[str, List[Turn]]:
        pass

    @abstractmethod
    async def archive_transcript(self, session_id: str, question_id: str, turns: List[Turn]) -> None:
        pass

    @abstractmethod
    async def get_archived_transcript(self, session_id: str, question_id: str) -> List[Turn]:
        pass

    @abstractmethod
    async def get_summaries(self, session_id: str) -> List[QuestionSummary]:
        pass

    @abstractmethod
    async def add_summary(self, session_id: str, summary: QuestionSummary) -> None:
        pass

    @abstractmethod
    async def get_pinned_context(self, session_id: str) -> Optional[PinnedContext]:
        pass

    @abstractmethod
    async def save_pinned_context(self, session_id: str, context: PinnedContext) -> None:
        pass
