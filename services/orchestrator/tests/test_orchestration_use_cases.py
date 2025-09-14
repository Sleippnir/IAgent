import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.orchestration_use_cases import OrchestrationUseCases
from app.domain.entities.session import Session, Question, PinnedContext, Turn
from app.domain.repositories.session_repository import SessionRepository

@pytest.fixture
def sample_pinned_context() -> PinnedContext:
    """Fixture to create a sample pinned context."""
    return PinnedContext(
        jd_digest="Senior Engineer role",
        candidate_digest="Experienced with Python",
    )

@pytest.fixture
def mock_session_repository(sample_pinned_context: PinnedContext) -> AsyncMock:
    """Fixture to create a mock session repository."""
    mock = AsyncMock(spec=SessionRepository)
    mock.get_questions = AsyncMock()
    mock.save_session = AsyncMock()
    mock.save_pinned_context = AsyncMock()
    mock.get_session = AsyncMock()
    mock.add_transcript_turn = AsyncMock()
    mock.get_transcript_turns = AsyncMock(return_value=[])
    mock.get_summaries = AsyncMock(return_value=[])
    mock.get_pinned_context = AsyncMock(return_value=sample_pinned_context)
    mock.save_questions = AsyncMock()
    return mock

@pytest.fixture
def sample_questions() -> list[Question]:
    """Fixture to create sample questions."""
    return [
        Question(role_id="test_role", question_id="q1", order_index=0, question_text="Question 1?"),
        Question(role_id="test_role", question_id="q2", order_index=1, question_text="Question 2?"),
    ]

@pytest.mark.asyncio
async def test_start_session(
    mock_session_repository: AsyncMock,
    sample_questions: list[Question]
):
    """Test the start_session use case."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    mock_session_repository.get_questions.return_value = sample_questions
    role_id = "test_role"

    # Act
    session = await use_cases.start_session(role_id=role_id)

    # Assert
    assert session is not None
    assert isinstance(session, Session)
    assert session.role_id == role_id
    assert session.status == "active"
    assert session.active_question_id == "q1" # First question should be active

    mock_session_repository.get_questions.assert_called_once_with(role_id)
    mock_session_repository.save_session.assert_called_once()
    mock_session_repository.save_pinned_context.assert_called_once()

@pytest.mark.asyncio
async def test_candidate_message_advances_on_skip(
    mock_session_repository: AsyncMock,
    sample_questions: list[Question]
):
    """Test that the session advances when the candidate says 'skip'."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    session_id = "test_session_id"
    active_session = Session(session_id=session_id, role_id="test_role", active_question_id="q1")

    mock_session_repository.get_session.return_value = active_session
    mock_session_repository.get_questions.return_value = sample_questions
    mock_session_repository.get_transcript_turns.return_value = []

    # Act
    response = await use_cases.candidate_message(session_id=session_id, text="skip")

    # Assert
    assert response["session_status"]["active_question_id"] == "q2"
    assert response["session_status"]["current_index"] == 0
    mock_session_repository.add_summary.assert_called_once()

@pytest.mark.asyncio
async def test_kickoff_scoring(
    mock_session_repository: AsyncMock,
    sample_questions: list[Question],
    sample_pinned_context: PinnedContext
):
    """Test the kickoff_scoring use case."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    session_id = "test_session_id"
    completed_session = Session(session_id=session_id, role_id="test_role", status="completed")

    mock_session_repository.get_session.return_value = completed_session
    mock_session_repository.get_questions.return_value = sample_questions
    mock_session_repository.get_summaries.return_value = []
    mock_session_repository.get_pinned_context.return_value = sample_pinned_context

    # Act
    payload = await use_cases.kickoff_scoring(session_id)

    # Assert
    assert payload["session_id"] == session_id
    assert payload["role_id"] == "test_role"
    assert "canonical_questions" in payload
    assert "question_summaries" in payload

@pytest.mark.asyncio
async def test_get_session_status(
    mock_session_repository: AsyncMock,
    sample_questions: list[Question]
):
    """Test the get_session_status use case."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    session_id = "test_session_id"
    active_session = Session(session_id=session_id, role_id="test_role", active_question_id="q1")

    mock_session_repository.get_session.return_value = active_session
    mock_session_repository.get_questions.return_value = sample_questions

    # Act
    status = await use_cases.get_session_status(session_id)

    # Assert
    assert status["session_id"] == session_id
    assert status["active_question_id"] == "q1"

@pytest.mark.asyncio
async def test_import_questions(mock_session_repository: AsyncMock):
    """Test the import_questions use case."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    role_id = "test_role"
    question_texts = ["What is your favorite color?", "What is the air-speed velocity of an unladen swallow?"]

    # Act
    count = await use_cases.import_questions(role_id, question_texts)

    # Assert
    assert count == 2
    mock_session_repository.save_questions.assert_called_once()
    saved_questions = mock_session_repository.save_questions.call_args[0][1]
    assert len(saved_questions) == 2
    assert saved_questions[0].question_text == question_texts[0]


@pytest.mark.asyncio
async def test_candidate_message_advances_after_two_turns(
    mock_session_repository: AsyncMock,
    sample_questions: list[Question]
):
    """Test that the session advances after two candidate turns."""
    # Arrange
    use_cases = OrchestrationUseCases(session_repository=mock_session_repository)
    session_id = "test_session_id"
    active_session = Session(session_id=session_id, role_id="test_role", active_question_id="q1")

    mock_session_repository.get_session.return_value = active_session
    mock_session_repository.get_questions.return_value = sample_questions

    # Simulate a stateful transcript
    transcript_turns = [Turn(sender="candidate", text="My first answer.")]

    def get_turns_side_effect(*args, **kwargs):
        return transcript_turns

    def add_turn_side_effect(sid, qid, turn):
        transcript_turns.append(turn)

    mock_session_repository.get_transcript_turns.side_effect = get_turns_side_effect
    mock_session_repository.add_transcript_turn.side_effect = add_turn_side_effect

    # Act
    response = await use_cases.candidate_message(session_id=session_id, text="My second answer.")

    # Assert
    assert response["session_status"]["active_question_id"] == "q2"
    assert response["session_status"]["current_index"] == 0
    mock_session_repository.add_summary.assert_called_once()
