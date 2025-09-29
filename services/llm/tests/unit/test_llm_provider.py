"""
Unit tests for LLM provider functions.
Tests the core LLM API calling functions with mocked responses.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.infrastructure.llm_provider import (
    call_openai_gpt5,
    call_google_gemini,
    call_openrouter_deepseek,
    load_interview_from_source,
    run_evaluations
)
from app.domain.entities.interview import Interview


class TestLLMProviderFunctions:
    """Test suite for LLM provider functions"""

    @pytest.fixture
    def sample_prompt(self):
        """Sample prompt for testing"""
        return "You are an expert interviewer."

    @pytest.fixture
    def sample_rubric(self):
        """Sample evaluation rubric"""
        return "Rate on technical skills (1-10), communication (1-10), culture fit (1-10)."

    @pytest.fixture
    def sample_transcript(self):
        """Sample interview transcript"""
        return "Interviewer: Tell me about yourself. Candidate: I'm a software engineer..."

    @pytest.fixture
    def sample_interview(self):
        """Sample interview object"""
        return Interview(
            interview_id="test-123",
            system_prompt="Test prompt",
            rubric="Test rubric",
            jd="Test job description",
            full_transcript="Test transcript"
        )

    @pytest.mark.asyncio
    async def test_call_openai_gpt5_success(self, sample_prompt, sample_rubric, sample_transcript):
        """Test successful OpenAI GPT-5 API call"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Excellent candidate with strong technical skills."

        with patch('app.infrastructure.llm_provider.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch('app.infrastructure.llm_provider.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test-key"
                mock_settings.OPENAI_MODEL = "gpt-5"
                mock_settings.DEFAULT_MAX_TOKENS = 2000
                mock_settings.DEFAULT_TEMPERATURE = 0.3

                result = await call_openai_gpt5(sample_prompt, sample_rubric, sample_transcript)

                assert result == "Excellent candidate with strong technical skills."
                mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_openai_gpt5_missing_api_key(self, sample_prompt, sample_rubric, sample_transcript):
        """Test OpenAI GPT-5 call with missing API key"""
        with patch('app.infrastructure.llm_provider.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = None

            result = await call_openai_gpt5(sample_prompt, sample_rubric, sample_transcript)

            assert "Error calling OpenAI API" in result
            assert "OPENAI_API_KEY not set" in result

    @pytest.mark.asyncio
    async def test_call_openai_gpt5_api_error(self, sample_prompt, sample_rubric, sample_transcript):
        """Test OpenAI GPT-5 call with API error"""
        with patch('app.infrastructure.llm_provider.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            with patch('app.infrastructure.llm_provider.settings') as mock_settings:
                mock_settings.OPENAI_API_KEY = "test-key"

                result = await call_openai_gpt5(sample_prompt, sample_rubric, sample_transcript)

                assert "Error calling OpenAI API: API Error" in result

    @pytest.mark.asyncio
    async def test_call_google_gemini_success(self, sample_prompt, sample_rubric, sample_transcript):
        """Test successful Google Gemini API call"""
        mock_response = Mock()
        mock_response.text = "Strong technical background, good communication skills."

        with patch('app.infrastructure.llm_provider.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            with patch('app.infrastructure.llm_provider.settings') as mock_settings:
                mock_settings.GOOGLE_API_KEY = "test-key"
                mock_settings.GEMINI_MODEL = "gemini-2.5-pro"

                result = await call_google_gemini(sample_prompt, sample_rubric, sample_transcript)

                assert result == "Strong technical background, good communication skills."
                mock_genai.configure.assert_called_once_with(api_key="test-key")
                mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_google_gemini_missing_api_key(self, sample_prompt, sample_rubric, sample_transcript):
        """Test Google Gemini call with missing API key"""
        with patch('app.infrastructure.llm_provider.settings') as mock_settings:
            mock_settings.GOOGLE_API_KEY = None

            result = await call_google_gemini(sample_prompt, sample_rubric, sample_transcript)

            assert "Error calling Google Gemini API" in result
            assert "GOOGLE_API_KEY not set" in result

    @pytest.mark.asyncio
    async def test_call_openrouter_deepseek_success(self, sample_prompt, sample_rubric, sample_transcript):
        """Test successful OpenRouter DeepSeek API call"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Solid candidate with room for growth."

        with patch('app.infrastructure.llm_provider.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch('app.infrastructure.llm_provider.settings') as mock_settings:
                mock_settings.OPENROUTER_API_KEY = "test-key"
                mock_settings.DEEPSEEK_MODEL = "deepseek/deepseek-chat-v3.1"
                mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
                mock_settings.DEFAULT_MAX_TOKENS = 2000
                mock_settings.DEFAULT_TEMPERATURE = 0.3

                result = await call_openrouter_deepseek(sample_prompt, sample_rubric, sample_transcript)

                assert result == "Solid candidate with room for growth."
                mock_openai.assert_called_once_with(
                    base_url="https://openrouter.ai/api/v1",
                    api_key="test-key"
                )

    @pytest.mark.asyncio
    async def test_call_openrouter_deepseek_missing_api_key(self, sample_prompt, sample_rubric, sample_transcript):
        """Test OpenRouter DeepSeek call with missing API key"""
        with patch('app.infrastructure.llm_provider.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = None

            result = await call_openrouter_deepseek(sample_prompt, sample_rubric, sample_transcript)

            assert "Error calling OpenRouter API" in result
            assert "OPENROUTER_API_KEY not set" in result

    def test_load_interview_from_source_file_success(self):
        """Test loading interview from file successfully"""
        mock_data = {
            "interview_id": "file-123",
            "system_prompt": "Test prompt",
            "rubric": "Test rubric",
            "jd": "Test JD",
            "full_transcript": "Test transcript"
        }

        with patch('builtins.open', mock_open_read(mock_data)):
            with patch('json.load', return_value=mock_data):
                result = load_interview_from_source('file', 'test_file.json')

                assert isinstance(result, Interview)
                assert result.interview_id == "file-123"
                assert result.system_prompt == "Test prompt"

    def test_load_interview_from_source_file_not_found(self):
        """Test loading interview from non-existent file"""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                load_interview_from_source('file', 'nonexistent.json')

    def test_load_interview_from_source_invalid_json(self):
        """Test loading interview from file with invalid JSON"""
        with patch('builtins.open', mock_open_read("invalid json")):
            with patch('json.load', side_effect=ValueError("Invalid JSON")):
                with pytest.raises(ValueError):
                    load_interview_from_source('file', 'invalid.json')

    def test_load_interview_from_source_unsupported_type(self):
        """Test loading interview with unsupported source type"""
        with pytest.raises(ValueError, match="Unsupported source type"):
            load_interview_from_source('unsupported', 'test')

    @patch('app.infrastructure.llm_provider.call_openai_gpt5')
    @patch('app.infrastructure.llm_provider.call_google_gemini')
    @patch('app.infrastructure.llm_provider.call_openrouter_deepseek')
    def test_run_evaluations(self, mock_deepseek, mock_gemini, mock_openai, sample_interview):
        """Test running evaluations on interview"""
        # Setup mocks - run_evaluations calls the functions directly, not as async
        mock_openai.return_value = "OpenAI evaluation result"
        mock_gemini.return_value = "Gemini evaluation result" 
        mock_deepseek.return_value = "DeepSeek evaluation result"

        result = run_evaluations(sample_interview)

        # Verify all LLM functions were called
        mock_openai.assert_called_once_with(
            sample_interview.system_prompt,
            sample_interview.rubric,
            sample_interview.full_transcript
        )
        mock_gemini.assert_called_once_with(
            sample_interview.system_prompt,
            sample_interview.rubric,
            sample_interview.full_transcript
        )
        mock_deepseek.assert_called_once_with(
            sample_interview.system_prompt,
            sample_interview.rubric,
            sample_interview.full_transcript
        )

        # Verify evaluations were set
        assert result.evaluation_1 == "OpenAI evaluation result"
        assert result.evaluation_2 == "Gemini evaluation result"
        assert result.evaluation_3 == "DeepSeek evaluation result"


def mock_open_read(data):
    """Helper function to mock file reading"""
    from unittest.mock import mock_open
    import json
    if isinstance(data, dict):
        return mock_open(read_data=json.dumps(data))
    else:
        return mock_open(read_data=data)