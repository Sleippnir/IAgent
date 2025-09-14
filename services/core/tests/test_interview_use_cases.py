import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from typing import List

from app.application.use_cases.interview_use_cases import InterviewUseCases
from app.domain.entities.interview import Interview
from app.domain.repositories.interview_repository import InterviewRepository

@pytest.fixture
def mock_interview_repository() -> AsyncMock:
    """Fixture to create a mock interview repository."""
    mock = AsyncMock(spec=InterviewRepository)
    mock.create = AsyncMock()
    mock.get = AsyncMock()
    mock.list = AsyncMock()
    mock.update = AsyncMock()
    return mock

@pytest.fixture
def sample_interview() -> Interview:
    """Fixture to create a sample interview."""
    return Interview(
        id="test_interview_id",
        candidate_id="test_candidate_id",
        position_id="test_position_id",
        status="scheduled",
        created_at=datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime(2023, 1, 1, 12, 0, 0),
    )

@pytest.mark.asyncio
async def test_create_interview(mock_interview_repository: AsyncMock):
    """Test the create_interview use case."""
    # Arrange
    use_cases = InterviewUseCases(repository=mock_interview_repository)
    candidate_id = "test_candidate_id"
    position_id = "test_position_id"

    # Act
    with patch('app.application.use_cases.interview_use_cases.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        await use_cases.create_interview(candidate_id=candidate_id, position_id=position_id)

    # Assert
    assert mock_interview_repository.create.call_count == 1
    call_args = mock_interview_repository.create.call_args[0][0]
    assert isinstance(call_args, Interview)
    assert call_args.candidate_id == candidate_id
    assert call_args.position_id == position_id
    assert call_args.status == "scheduled"

@pytest.mark.asyncio
async def test_get_interview(mock_interview_repository: AsyncMock, sample_interview: Interview):
    """Test the get_interview use case."""
    # Arrange
    use_cases = InterviewUseCases(repository=mock_interview_repository)
    mock_interview_repository.get.return_value = sample_interview
    interview_id = "test_interview_id"

    # Act
    result = await use_cases.get_interview(interview_id)

    # Assert
    mock_interview_repository.get.assert_called_once_with(interview_id)
    assert result == sample_interview

@pytest.mark.asyncio
async def test_list_interviews(mock_interview_repository: AsyncMock, sample_interview: Interview):
    """Test the list_interviews use case."""
    # Arrange
    use_cases = InterviewUseCases(repository=mock_interview_repository)
    mock_interview_repository.list.return_value = [sample_interview]

    # Act
    result = await use_cases.list_interviews()

    # Assert
    mock_interview_repository.list.assert_called_once()
    assert result == [sample_interview]

@pytest.mark.asyncio
async def test_update_interview_status(mock_interview_repository: AsyncMock, sample_interview: Interview):
    """Test the update_interview_status use case."""
    # Arrange
    use_cases = InterviewUseCases(repository=mock_interview_repository)
    mock_interview_repository.get.return_value = sample_interview
    mock_interview_repository.update.return_value = sample_interview
    interview_id = "test_interview_id"
    new_status = "completed"

    # Act
    with patch('app.application.use_cases.interview_use_cases.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 5, 0)
        result = await use_cases.update_interview_status(interview_id, new_status)

    # Assert
    mock_interview_repository.get.assert_called_once_with(interview_id)
    mock_interview_repository.update.assert_called_once()

    # Check the actual call arguments for update
    update_call_args = mock_interview_repository.update.call_args[0]
    assert update_call_args[0] == interview_id
    updated_interview = update_call_args[1]
    assert isinstance(updated_interview, Interview)
    assert updated_interview.status == new_status
    assert updated_interview.completed_at is not None
    assert result is not None
    assert result.status == new_status
