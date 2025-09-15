from __future__ import annotations
import time, uuid, json, hashlib
from typing import List, Dict, Optional, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Interview Orchestrator (Option C)")

# -------------------------
# In-memory demo storage
# -------------------------
DB = {
    "sessions": {},          # session_id -> Session
    "questions": {},         # role_id -> list[Question] sorted by order_index
    "transcript": {},        # (session_id, question_id) -> list[Turn]
    "archived_transcripts": {}, # (session_id, question_id) -> list[Turn]
    "summaries": {},         # session_id -> list[QuestionSummary]
    "pinned_context": {},    # session_id -> PinnedContext
    "rubrics": {},           # session_id -> Rubric text
}

# -------------------------
# Data models
# -------------------------
class Question(BaseModel):
    role_id: str
    question_id: str
    order_index: int
    question_text: str

class Turn(BaseModel):
    sender: Literal["interviewer", "candidate"]
    text: str
    ts: float = Field(default_factory=lambda: time.time())

class QuestionSummary(BaseModel):
    question_id: str
    outcome: Literal["answered", "skipped"]
    bullet_summary: List[str]
    evidence_snippets: List[str] = []
    confidence: float = 0.5
    ts: float = Field(default_factory=lambda: time.time())

class Session(BaseModel):
    session_id: str
    role_id: str
    status: Literal["active", "completed"] = "active"
    current_index: int = -1  # index of last COMPLETED question
    active_question_id: Optional[str] = None

class PinnedContext(BaseModel):
    jd_digest: str = ""
    candidate_digest: str = ""
    linkedin_digest: str = ""
    extra_notes: str = ""

# -------------------------
# Utilities
# -------------------------
def qhash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def get_questions(role_id: str) -> List[Question]:
    if role_id not in DB["questions"]:
        return []
    return sorted(DB["questions"][role_id], key=lambda q: q.order_index)

def get_active_question(sess: Session) -> Optional[Question]:
    if not sess.active_question_id:
        return None
    for q in get_questions(sess.role_id):
        if q.question_id == sess.active_question_id:
            return q
    return None

def get_next_question(sess: Session) -> Optional[Question]:
    qs = get_questions(sess.role_id)
    nxt_idx = sess.current_index + 1
    if nxt_idx < len(qs):
        return qs[nxt_idx]
    return None

def transcript_key(session_id: str, question_id: str) -> str:
    return f"{session_id}::{question_id}"

def ensure_transcript_list(session_id: str, question_id: str) -> List[Turn]:
    key = transcript_key(session_id, question_id)
    if key not in DB["transcript"]:
        DB["transcript"][key] = []
    return DB["transcript"][key]

def append_turn(session_id: str, question_id: str, sender: str, text: str):
    ensure_transcript_list(session_id, question_id).append(Turn(sender=sender, text=text))

def clear_transcript(session_id: str, question_id: str):
    DB["transcript"].pop(transcript_key(session_id, question_id), None)

def list_transcripts_for_session(session_id: str) -> Dict[str, List[Turn]]:
    out = {}
    for key, turns in DB["transcript"].items():
        if key.startswith(session_id + "::"):
            out[key.split("::")[1]] = turns
    return out

# -------------------------
# Interviewer System Prompt (saves context summary)
# -------------------------
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
     • 3-6 bullets covering: example, scope (team/timeline/role), tools, metrics/outcomes, trade-offs/lessons.
     • up to 2 short evidence snippets (<= 30 words each).
     • confidence in [0.0, 1.0] for completeness/specificity.
   - Mark the question outcome and request the next question.
5) When no questions remain, conclude: “Interview completed. Thank you.”

Rules:
- Do NOT reveal future questions or the full list.
- Keep follow-ups scoped to the current question.
- Be concise and professional; exactly one follow-up at a time.
"""

# -------------------------
# LLM client shims (replace with your providers)
# -------------------------
class ToolResult(BaseModel):
    name: str
    payload: dict

class LLMResult(BaseModel):
    assistant_text: str = ""
    tool_calls: List[ToolResult] = []

class InterviewerLLMClient:
    """
    Replace this shim with your actual SDK call.
    The idea:
    - You pass messages + tools.
    - The model may return assistant text and/or a sequence of tool calls.
    """
    def run(self, messages: List[dict], tools: List[dict]) -> LLMResult:
        # DEMO behavior: If no active question, ask for it;
        # otherwise, ask the current question (or a generic follow-up).
        # In production, you’ll use a function-calling model and remove this stub.
        sys = next((m for m in messages if m["role"] == "system"), None)
        ctx = next((m for m in messages if m["role"] == "system" and m.get("name") == "pinned_context"), None)

        # Simple heuristic: if last user message came from candidate, ask one follow-up;
        # otherwise, ask the canonical question.
        last_user = [m for m in messages if m["role"] == "user"]
        last_candidate = last_user[-1]["content"] if last_user else ""

        # We cannot truly track active question here; the orchestrator handles that.
        # We'll simulate: if last_candidate exists => follow-up; else => ask question.
        if last_candidate:
            return LLMResult(assistant_text="Thanks. Could you share one concrete metric or outcome from that experience?")
        else:
            return LLMResult(assistant_text="To begin, could you walk me through your approach to this topic?")

interviewer_model = InterviewerLLMClient()

# -------------------------
# Public API models
# -------------------------
class ImportQuestionsRequest(BaseModel):
    role_id: str
    questions: List[str]

class StartSessionRequest(BaseModel):
    role_id: str
    jd_digest: str = ""
    candidate_digest: str = ""
    linkedin_digest: str = ""
    extra_notes: str = ""
    rubric: str = ""  # Stored and used by post-interview reasoners

class StartSessionResponse(BaseModel):
    session_id: str
    first_question: Optional[str]

class CandidateMessageRequest(BaseModel):
    session_id: str
    text: str

class SessionStatusResponse(BaseModel):
    session_id: str
    role_id: str
    status: str
    active_question_id: Optional[str]
    current_index: int
    summaries_count: int

# -------------------------
# API: import canonical questions
# -------------------------
@app.post("/roles/import")
def import_questions(req: ImportQuestionsRequest):
    qs = []
    for idx, qtext in enumerate(req.questions):
        qid = qhash(qtext)
        qs.append(Question(role_id=req.role_id, question_id=qid, order_index=idx, question_text=qtext))
    DB["questions"][req.role_id] = qs
    return {"ok": True, "count": len(qs)}

# -------------------------
# API: start session
# -------------------------
@app.post("/sessions/start", response_model=StartSessionResponse)
def start_session(req: StartSessionRequest):
    if req.role_id not in DB["questions"] or not DB["questions"][req.role_id]:
        raise HTTPException(400, "No questions for role_id")

    sid = uuid.uuid4().hex
    sess = Session(session_id=sid, role_id=req.role_id)
    DB["sessions"][sid] = sess

    DB["pinned_context"][sid] = PinnedContext(
        jd_digest=req.jd_digest,
        candidate_digest=req.candidate_digest,
        linkedin_digest=req.linkedin_digest,
        extra_notes=req.extra_notes,
    )
    DB["summaries"][sid] = []
    DB["rubrics"][sid] = req.rubric or ""

    # Prime the first question as "active"
    q = get_next_question(sess)
    if q:
        sess.active_question_id = q.question_id
    return StartSessionResponse(session_id=sid, first_question=q.question_text if q else None)

# -------------------------
# Internal: build LLM messages (Option C windowing)
# -------------------------
def build_messages_for_llm(sess: Session) -> List[dict]:
    msgs = [{"role": "system", "content": INTERVIEWER_SYSTEM_PROMPT}]
    # Pinned context (summaries of prior questions + JD/CV)
    pinned = {
        "context_version": 1,
        "role_id": sess.role_id,
        "jd_digest": DB["pinned_context"][sess.session_id].jd_digest,
        "candidate_digest": DB["pinned_context"][sess.session_id].candidate_digest,
        "linkedin_digest": DB["pinned_context"][sess.session_id].linkedin_digest,
        "extra_notes": DB["pinned_context"][sess.session_id].extra_notes,
        "prior_question_summaries": [s.dict() for s in DB["summaries"][sess.session_id]],
    }
    msgs.append({"role": "system", "name": "pinned_context", "content": json.dumps(pinned)})

    # Only current question's raw turns
    q = get_active_question(sess)
    if q:
        turns = ensure_transcript_list(sess.session_id, q.question_id)
        for t in turns[-20:]:  # cap window
            if t.sender == "interviewer":
                msgs.append({"role": "assistant", "content": t.text})
            else:
                msgs.append({"role": "user", "content": t.text})
    return msgs

# -------------------------
# Orchestration helpers
# -------------------------
def mark_question_answered_or_skipped(sess: Session, outcome: Literal["answered", "skipped"], auto_summary=False):
    q = get_active_question(sess)
    if not q:
        return
    # Auto-create a minimal summary if needed (fallback)
    if auto_summary:
        bullets = ["Candidate opted to skip." if outcome == "skipped" else "Answered briefly; details limited."]
        summary = QuestionSummary(
            question_id=q.question_id,
            outcome=outcome,
            bullet_summary=bullets,
            evidence_snippets=[],
            confidence=0.4 if outcome == "answered" else 0.2,
        )
    else:
        # For demo, synthesize from last 2 candidate turns
        turns = ensure_transcript_list(sess.session_id, q.question_id)
        last_cand = [t.text for t in turns if t.sender == "candidate"][-2:]
        bullets = ["; ".join(last_cand)] if last_cand else ["(no candidate content)"]
        summary = QuestionSummary(
            question_id=q.question_id,
            outcome=outcome,
            bullet_summary=bullets,
            evidence_snippets=last_cand[:1],
            confidence=0.6 if outcome == "answered" else 0.2,
        )

    DB["summaries"][sess.session_id].append(summary)

    # Archive the full raw transcript before clearing it from the active pool.
    key = transcript_key(sess.session_id, q.question_id)
    if key in DB["transcript"]:
        DB["archived_transcripts"][key] = DB["transcript"][key]

    # finalize: clear transcript and advance pointer
    clear_transcript(sess.session_id, q.question_id)
    sess.current_index += 1
    sess.active_question_id = None

    nxt = get_next_question(sess)
    if nxt:
        sess.active_question_id = nxt.question_id
    else:
        sess.status = "completed"

def push_interviewer_text(sess: Session, text: str):
    q = get_active_question(sess)
    if not q:
        return
    append_turn(sess.session_id, q.question_id, "interviewer", text)

# -------------------------
# API: candidate sends a message (drives the loop)
# -------------------------
@app.post("/sessions/candidate_message")
def candidate_message(req: CandidateMessageRequest):
    sess = DB["sessions"].get(req.session_id)
    if not sess:
        raise HTTPException(404, "session_id not found")
    if sess.status != "active":
        raise HTTPException(400, "Session is not active")

    # Ensure an active question exists
    if not sess.active_question_id:
        nxt = get_next_question(sess)
        if not nxt:
            raise HTTPException(400, "No questions remain")
        sess.active_question_id = nxt.question_id

    # Log candidate turn
    append_turn(sess.session_id, sess.active_question_id, "candidate", req.text)

    # Build messages for interviewer LLM
    msgs = build_messages_for_llm(sess)

    # Call interviewer model (with tools in real system)
    tools = [
        {"name": "log_message"},
        {"name": "get_or_set_current_question"},
        {"name": "summarize_and_mark"},
        {"name": "request_next_question"},
        {"name": "conclude_interview"},
    ]
    result = interviewer_model.run(msgs, tools)

    # Log/emit interviewer text if present
    if result.assistant_text:
        push_interviewer_text(sess, result.assistant_text)

    # Heuristics: if candidate said 'skip', mark skipped; else if the interviewer asked for a metric and we already have >=2 candidate turns, mark answered.
    lc = req.text.strip().lower()
    if lc in {"skip", "pass", "next, please"}:
        mark_question_answered_or_skipped(sess, "skipped", auto_summary=True)
    else:
        # Example auto-resolve after some back-and-forth; replace with model tool-calls in production.
        turns = ensure_transcript_list(sess.session_id, sess.active_question_id)
        cand_count = len([t for t in turns if t.sender == "candidate"])
        if cand_count >= 2:
            mark_question_answered_or_skipped(sess, "answered", auto_summary=False)

    # Return current interviewer message and status
    q = get_active_question(sess)
    return {
        "assistant_text": result.assistant_text,
        "session_status": SessionStatusResponse(
            session_id=sess.session_id,
            role_id=sess.role_id,
            status=sess.status,
            active_question_id=q.question_id if q else None,
            current_index=sess.current_index,
            summaries_count=len(DB["summaries"][sess.session_id]),
        ).dict(),
    }

# -------------------------
# API: get status
# -------------------------
@app.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
def session_status(session_id: str):
    sess = DB["sessions"].get(session_id)
    if not sess:
        raise HTTPException(404, "session_id not found")
    q = get_active_question(sess)
    return SessionStatusResponse(
        session_id=session_id,
        role_id=sess.role_id,
        status=sess.status,
        active_question_id=q.question_id if q else None,
        current_index=sess.current_index,
        summaries_count=len(DB["summaries"][session_id]),
    )

# -------------------------
# API: conclude + scoring handoff (3 “reasoning” LLMs)
# -------------------------
class ScoringKickoffResponse(BaseModel):
    session_id: str
    packaged_payload: dict

@app.post("/sessions/{session_id}/score", response_model=ScoringKickoffResponse)
def kickoff_scoring(session_id: str):
    sess = DB["sessions"].get(session_id)
    if not sess:
        raise HTTPException(404, "session_id not found")
    if sess.status != "completed":
        raise HTTPException(400, "Interview must be completed before scoring")

    role_id = sess.role_id
    questions = get_questions(role_id)
    
    # Gather FULL raw transcripts from the archive.
    transcripts: Dict[str, List[dict]] = {}
    transcripts.update({
        q.question_id: [t.dict() for t in DB["archived_transcripts"].get(transcript_key(session_id, q.question_id), [])]
        for q in questions
    })

    payload = {
        "session_id": session_id,
        "role_id": role_id,
        "pinned_context": DB["pinned_context"][session_id].dict(),
        "rubric": DB["rubrics"].get(session_id, ""),
        "canonical_questions": [q.dict() for q in questions],
        "question_summaries": [s.dict() for s in DB["summaries"][session_id]],
        "full_transcripts": transcripts, # This now contains the complete, archived conversations
    }

    # TODO: send `payload` to your three reasoning models
    # examples:
    #   send_to_reasoner("gpt-REASONER-1", payload)
    #   send_to_reasoner("claude-REASONER-2", payload)
    #   send_to_reasoner("local-deep-reasoner", payload)
    # Combine / ensemble their scores server-side.

    return ScoringKickoffResponse(session_id=session_id, packaged_payload=payload)

# -------------------------
# Demo helpers: bootstrap role & run
# -------------------------
@app.post("/demo/bootstrap")
def demo_bootstrap():
    role_id = "senior_software_engineer"
    questions = [
        "Describe a complex technical challenge you faced and how you solved it.",
        "How do you approach mentoring junior developers?",
        "What is your process for designing a new system component?",
    ]
    import_questions(ImportQuestionsRequest(role_id=role_id, questions=questions))

    sess = start_session(StartSessionRequest(
        role_id=role_id,
        jd_digest="We seek an SSE with 5+ years in Python/Java, strong DS/Algo, cloud exp.",
        candidate_digest="Candidate X: ex-ABC Corp, built event pipeline, led 4 engineers.",
        linkedin_digest="Lead engineer; OSS contributor; GCP cert.",
        extra_notes="Focus on distributed systems & mentoring.",
        rubric="Score for specificity, metrics, complexity handling, ownership, reflection."
    ))
    return {"role_id": role_id, "session": sess.dict()}

