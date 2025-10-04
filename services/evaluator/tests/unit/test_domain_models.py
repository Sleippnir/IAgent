"""
Unit tests for domain models.
Tests the Pydantic models and data validation.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.domain.models import (
    ModelType,
    Message,
    GenerateRequest,
    GenerateResponse,
    PromptContext,
    PromptRequest
)


class TestModelType:
    """Test suite for ModelType enum"""

    def test_model_type_values(self):
        """Test that ModelType enum has expected values"""
        assert ModelType.GPT_4 == "gpt-4"
        assert ModelType.GPT_3_5 == "gpt-3.5-turbo"
        assert ModelType.CLAUDE == "claude-3"
        assert ModelType.LLAMA == "llama-2"

    def test_model_type_iteration(self):
        """Test iterating over ModelType enum"""
        model_types = list(ModelType)
        assert len(model_types) == 4
        assert ModelType.GPT_4 in model_types


class TestMessage:
    """Test suite for Message model"""

    def test_message_creation_valid(self):
        """Test creating a valid Message"""
        message = Message(
            role="user",
            content="Hello, how are you?",
            timestamp=datetime.now()
        )
        
        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert isinstance(message.timestamp, datetime)

    def test_message_creation_minimal(self):
        """Test creating Message with minimal required fields"""
        message = Message(
            role="assistant",
            content="I'm doing well, thank you!"
        )
        
        assert message.role == "assistant"
        assert message.content == "I'm doing well, thank you!"
        assert message.timestamp is None

    def test_message_json_serialization(self):
        """Test Message JSON serialization"""
        timestamp = datetime(2025, 9, 29, 12, 0, 0)
        message = Message(
            role="system",
            content="You are a helpful assistant",
            timestamp=timestamp
        )
        
        json_data = message.model_dump()
        assert json_data["role"] == "system"
        assert json_data["content"] == "You are a helpful assistant"
        assert json_data["timestamp"] == timestamp

    def test_message_invalid_data(self):
        """Test Message with invalid data"""
        with pytest.raises(ValidationError):
            Message()  # Missing required fields


class TestGenerateRequest:
    """Test suite for GenerateRequest model"""

    def test_generate_request_valid(self):
        """Test creating a valid GenerateRequest"""
        request = GenerateRequest(
            text="Generate a story about AI",
            session_id="session-123",
            context={"user_id": "user-456"},
            max_tokens=1500,
            temperature=0.8,
            model=ModelType.GPT_4,
            system_prompt="You are a creative writer"
        )
        
        assert request.text == "Generate a story about AI"
        assert request.session_id == "session-123"
        assert request.context == {"user_id": "user-456"}
        assert request.max_tokens == 1500
        assert request.temperature == 0.8
        assert request.model == ModelType.GPT_4
        assert request.system_prompt == "You are a creative writer"

    def test_generate_request_minimal(self):
        """Test creating GenerateRequest with minimal fields"""
        request = GenerateRequest(
            text="Hello world",
            session_id="session-789"
        )
        
        assert request.text == "Hello world"
        assert request.session_id == "session-789"
        assert request.context is None
        assert request.max_tokens == 1000  # Default value
        assert request.temperature == 0.7  # Default value
        assert request.model == ModelType.GPT_4  # Default value

    def test_generate_request_with_messages(self):
        """Test GenerateRequest with message history"""
        messages = [
            Message(role="user", content="What is Python?"),
            Message(role="assistant", content="Python is a programming language")
        ]
        
        request = GenerateRequest(
            text="Tell me more about Python frameworks",
            session_id="session-999",
            messages=messages
        )
        
        assert len(request.messages) == 2
        assert request.messages[0].role == "user"
        assert request.messages[1].role == "assistant"

    def test_generate_request_invalid_data(self):
        """Test GenerateRequest with invalid data"""
        with pytest.raises(ValidationError):
            GenerateRequest()  # Missing required fields


class TestGenerateResponse:
    """Test suite for GenerateResponse model"""

    def test_generate_response_valid(self):
        """Test creating a valid GenerateResponse"""
        timestamp = datetime.now()
        response = GenerateResponse(
            generated_text="Once upon a time...",
            session_id="session-123",
            timestamp=timestamp,
            processing_time=1.5,
            model_used="gpt-4",
            tokens_used=150,
            metadata={"confidence": 0.95}
        )
        
        assert response.generated_text == "Once upon a time..."
        assert response.session_id == "session-123"
        assert response.timestamp == timestamp
        assert response.processing_time == 1.5
        assert response.model_used == "gpt-4"
        assert response.tokens_used == 150
        assert response.metadata == {"confidence": 0.95}

    def test_generate_response_minimal(self):
        """Test creating GenerateResponse with minimal fields"""
        timestamp = datetime.now()
        response = GenerateResponse(
            generated_text="Hello!",
            session_id="session-456",
            timestamp=timestamp,
            processing_time=0.5,
            model_used="gpt-3.5-turbo"
        )
        
        assert response.generated_text == "Hello!"
        assert response.session_id == "session-456"
        assert response.tokens_used is None
        assert response.metadata is None

    def test_generate_response_json_serialization(self):
        """Test GenerateResponse JSON serialization with datetime"""
        timestamp = datetime(2025, 9, 29, 15, 30, 0)
        response = GenerateResponse(
            generated_text="Test response",
            session_id="session-789",
            timestamp=timestamp,
            processing_time=2.0,
            model_used="claude-3"
        )
        
        json_data = response.model_dump()
        assert json_data["timestamp"] == timestamp
        assert json_data["processing_time"] == 2.0

    def test_generate_response_invalid_data(self):
        """Test GenerateResponse with invalid data"""
        with pytest.raises(ValidationError):
            GenerateResponse()  # Missing required fields


class TestPromptContext:
    """Test suite for PromptContext model"""

    def test_prompt_context_empty(self):
        """Test creating empty PromptContext"""
        context = PromptContext()
        
        assert context.conversation_history == []
        assert context.user_preferences is None
        assert context.session_metadata is None

    def test_prompt_context_with_history(self):
        """Test PromptContext with conversation history"""
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!")
        ]
        
        context = PromptContext(
            conversation_history=messages,
            user_preferences={"language": "english"},
            session_metadata={"start_time": "2025-09-29T12:00:00"}
        )
        
        assert len(context.conversation_history) == 2
        assert context.user_preferences["language"] == "english"
        assert context.session_metadata["start_time"] == "2025-09-29T12:00:00"


class TestPromptRequest:
    """Test suite for PromptRequest model"""

    def test_prompt_request_minimal(self):
        """Test creating minimal PromptRequest"""
        request = PromptRequest(prompt="Tell me a joke")
        
        assert request.prompt == "Tell me a joke"
        assert request.context is None
        assert request.generation_config is None

    def test_prompt_request_with_context(self):
        """Test PromptRequest with context"""
        context = PromptContext(
            conversation_history=[
                Message(role="user", content="Previous message")
            ],
            user_preferences={"tone": "friendly"}
        )
        
        request = PromptRequest(
            prompt="Continue the conversation",
            context=context,
            generation_config={"temperature": 0.9, "max_tokens": 500}
        )
        
        assert request.prompt == "Continue the conversation"
        assert len(request.context.conversation_history) == 1
        assert request.context.user_preferences["tone"] == "friendly"
        assert request.generation_config["temperature"] == 0.9

    def test_prompt_request_invalid_data(self):
        """Test PromptRequest with invalid data"""
        with pytest.raises(ValidationError):
            PromptRequest()  # Missing required prompt field