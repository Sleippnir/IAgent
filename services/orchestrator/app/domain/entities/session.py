from __future__ import annotations
import time
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

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
