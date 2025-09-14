from typing import Optional
from pydantic import BaseModel

class StartSessionRequest(BaseModel):
    role_id: str
    jd_digest: str = ""
    candidate_digest: str = ""
    linkedin_digest: str = ""
    extra_notes: str = ""
    rubric: str = ""

from typing import List

class StartSessionResponse(BaseModel):
    session_id: str
    first_question: Optional[str]

class ImportQuestionsRequest(BaseModel):
    role_id: str
    questions: List[str]

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

from typing import Dict

class CandidateMessageResponse(BaseModel):
    assistant_text: str
    session_status: SessionStatusResponse

class ScoringKickoffResponse(BaseModel):
    session_id: str
    packaged_payload: Dict
