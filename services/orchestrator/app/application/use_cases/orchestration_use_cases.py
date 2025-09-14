import uuid
from typing import List, Optional
import hashlib
import json
from ...domain.entities.session import Session, Question, PinnedContext, Turn, QuestionSummary
from ...domain.repositories.session_repository import SessionRepository
from typing import Literal

INTERVIEWER_SYSTEM_PROMPT = """You are the INTERVIEWER. Conduct the interview one canonical question at a time.

Protocol for each canonical question:
1) Fetch the active question (or request the next if none).
2) Ask the candidate that question.
3) Run a focused inner dialog on THIS question only:
   - Ask a single concise follow-up per turn to elicit specifics, metrics, examples, trade-offs.
   - If the candidate asks for rephrasing, do so.
   - If the candidate says "skip", confirm and proceed to summarize.
4) When sufficiently answered OR skipped:
   - Produce a summary with:
     • 3–6 bullets covering: example, scope (team/timeline/role), tools, metrics/outcomes, trade-offs/lessons.
     • up to 2 short evidence snippets (<= 30 words each).
     • confidence in [0.0, 1.0] for completeness/specificity.
   - Mark the question outcome and request the next question.
5) When no questions remain, conclude: “Interview completed. Thank you.”

Rules:
- Do NOT reveal future questions or the full list.
- Keep follow-ups scoped to the current question.
- Be concise and professional; exactly one follow-up at a time.
"""

# LLM client shim
class LLMResult(object):
    def __init__(self, assistant_text: str = ""):
        self.assistant_text = assistant_text

class InterviewerLLMClient:
    def run(self, messages: List[dict], tools: List[dict]) -> LLMResult:
        return LLMResult(assistant_text="Thanks. Could you share one concrete metric or outcome from that experience?")

interviewer_model = InterviewerLLMClient()

def get_active_question(active_question_id: str, questions: List[Question]) -> Optional[Question]:
    """Gets the active question from a list of questions."""
    if not active_question_id:
        return None
    for q in questions:
        if q.question_id == active_question_id:
            return q
    return None

def get_next_question(current_index: int, questions: List[Question]) -> Optional[Question]:
    """Gets the next question in the list."""
    next_index = current_index + 1
    if next_index < len(questions):
        return questions[next_index]
    return None

def qhash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

class OrchestrationUseCases:
    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository
        self.llm_client = InterviewerLLMClient()

    async def start_session(
        self,
        role_id: str,
        jd_digest: str = "",
        candidate_digest: str = "",
        linkedin_digest: str = "",
        extra_notes: str = "",
        rubric: str = "",
    ) -> Session:
        """Starts a new interview session."""
        questions = await self.session_repository.get_questions(role_id)
        if not questions:
            raise ValueError("No questions found for the specified role_id")

        session_id = uuid.uuid4().hex
        session = Session(session_id=session_id, role_id=role_id)

        pinned_context = PinnedContext(
            jd_digest=jd_digest,
            candidate_digest=candidate_digest,
            linkedin_digest=linkedin_digest,
            extra_notes=extra_notes,
        )

        await self.session_repository.save_pinned_context(session_id, pinned_context)

        # Prime the first question
        first_question = get_next_question(session.current_index, questions)
        if first_question:
            session.active_question_id = first_question.question_id

        await self.session_repository.save_session(session)

        return session

    async def kickoff_scoring(self, session_id: str) -> dict:
        """Kicks off the scoring process for a completed interview."""
        session = await self.session_repository.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status != "completed":
            raise ValueError("Interview must be completed before scoring")

        questions = await self.session_repository.get_questions(session.role_id)
        summaries = await self.session_repository.get_summaries(session.session_id)
        pinned_context = await self.session_repository.get_pinned_context(session.session_id)

        # In a real system, we would get the full archived transcripts.
        # For now, we'll just use the summaries.

        payload = {
            "session_id": session_id,
            "role_id": session.role_id,
            "pinned_context": pinned_context.model_dump() if pinned_context else {},
            "rubric": "", # This should be stored and retrieved
            "canonical_questions": [q.model_dump() for q in questions],
            "question_summaries": [s.model_dump() for s in summaries],
            "full_transcripts": {}, # Placeholder
        }

        # TODO: Send payload to evaluation-reporting service

        return payload

    async def get_session_status(self, session_id: str) -> dict:
        """Gets the status of a session."""
        session = await self.session_repository.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        questions = await self.session_repository.get_questions(session.role_id)
        active_q = get_active_question(session.active_question_id, questions)
        summaries = await self.session_repository.get_summaries(session_id)

        return {
            "session_id": session.session_id,
            "role_id": session.role_id,
            "status": session.status,
            "active_question_id": active_q.question_id if active_q else None,
            "current_index": session.current_index,
            "summaries_count": len(summaries),
        }

    async def import_questions(self, role_id: str, questions_text: List[str]) -> int:
        """Imports a list of questions for a role."""
        questions = []
        for idx, qtext in enumerate(questions_text):
            qid = qhash(qtext)
            questions.append(Question(role_id=role_id, question_id=qid, order_index=idx, question_text=qtext))

        await self.session_repository.save_questions(role_id, questions)
        return len(questions)

    async def _build_messages_for_llm(self, session: Session) -> List[dict]:
        msgs = [{"role": "system", "content": INTERVIEWER_SYSTEM_PROMPT}]

        pinned_context = await self.session_repository.get_pinned_context(session.session_id)
        summaries = await self.session_repository.get_summaries(session.session_id)

        pinned = {
            "context_version": 1,
            "role_id": session.role_id,
            "jd_digest": pinned_context.jd_digest if pinned_context else "",
            "candidate_digest": pinned_context.candidate_digest if pinned_context else "",
            "linkedin_digest": pinned_context.linkedin_digest if pinned_context else "",
            "extra_notes": pinned_context.extra_notes if pinned_context else "",
            "prior_question_summaries": [s.model_dump() for s in summaries],
        }
        msgs.append({"role": "system", "name": "pinned_context", "content": json.dumps(pinned)})

        # Only current question's raw turns
        if session.active_question_id:
            turns = await self.session_repository.get_transcript_turns(session.session_id, session.active_question_id)
            for t in turns[-20:]:  # cap window
                if t.sender == "interviewer":
                    msgs.append({"role": "assistant", "content": t.text})
                else:
                    msgs.append({"role": "user", "content": t.text})
        return msgs

    async def _mark_question_answered_or_skipped(
        self, session: Session, outcome: Literal["answered", "skipped"], auto_summary: bool = False
    ):
        questions = await self.session_repository.get_questions(session.role_id)
        active_question = get_active_question(session.active_question_id, questions)
        if not active_question:
            return

        # Auto-create a minimal summary if needed
        if auto_summary:
            bullets = ["Candidate opted to skip." if outcome == "skipped" else "Answered briefly; details limited."]
            summary = QuestionSummary(
                question_id=active_question.question_id,
                outcome=outcome,
                bullet_summary=bullets,
                evidence_snippets=[],
                confidence=0.4 if outcome == "answered" else 0.2,
            )
        else:
            # For demo, synthesize from last 2 candidate turns
            turns = await self.session_repository.get_transcript_turns(session.session_id, active_question.question_id)
            last_cand = [t.text for t in turns if t.sender == "candidate"][-2:]
            bullets = ["; ".join(last_cand)] if last_cand else ["(no candidate content)"]
            summary = QuestionSummary(
                question_id=active_question.question_id,
                outcome=outcome,
                bullet_summary=bullets,
                evidence_snippets=last_cand[:1],
                confidence=0.6 if outcome == "answered" else 0.2,
            )

        await self.session_repository.add_summary(session.session_id, summary)

        # Archive the full raw transcript
        turns_to_archive = await self.session_repository.get_transcript_turns(session.session_id, active_question.question_id)
        await self.session_repository.archive_transcript(session.session_id, active_question.question_id, turns_to_archive)
        await self.session_repository.clear_transcript(session.session_id, active_question.question_id)

        # Advance to the next question
        session.current_index += 1
        next_question = get_next_question(session.current_index, questions)
        if next_question:
            session.active_question_id = next_question.question_id
        else:
            session.status = "completed"
            session.active_question_id = None

    async def candidate_message(self, session_id: str, text: str) -> dict:
        session = await self.session_repository.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        if session.status != "active":
            raise ValueError("Session is not active")

        questions = await self.session_repository.get_questions(session.role_id)
        if not session.active_question_id:
            next_q = get_next_question(session.current_index, questions)
            if not next_q:
                raise ValueError("No questions remain")
            session.active_question_id = next_q.question_id

        # Log candidate turn
        await self.session_repository.add_transcript_turn(
            session_id, session.active_question_id, Turn(sender="candidate", text=text)
        )

        # Build messages and call LLM
        messages = await self._build_messages_for_llm(session)
        tools = [] # Placeholder for tool definitions
        result = self.llm_client.run(messages, tools)

        # Log interviewer turn
        if result.assistant_text:
            await self.session_repository.add_transcript_turn(
                session_id,
                session.active_question_id,
                Turn(sender="interviewer", text=result.assistant_text),
            )

        # Heuristics for auto-advancing (replace with real tool calls)
        lc_text = text.strip().lower()
        if lc_text in {"skip", "pass", "next, please"}:
            await self._mark_question_answered_or_skipped(session, "skipped", auto_summary=True)
        else:
            turns = await self.session_repository.get_transcript_turns(session_id, session.active_question_id)
            cand_count = len([t for t in turns if t.sender == "candidate"])
            if cand_count >= 2:
                await self._mark_question_answered_or_skipped(session, "answered")

        await self.session_repository.save_session(session)

        active_q = get_active_question(session.active_question_id, questions)
        summaries = await self.session_repository.get_summaries(session_id)

        return {
            "assistant_text": result.assistant_text,
            "session_status": {
                "session_id": session.session_id,
                "role_id": session.role_id,
                "status": session.status,
                "active_question_id": active_q.question_id if active_q else None,
                "current_index": session.current_index,
                "summaries_count": len(summaries),
            },
        }
