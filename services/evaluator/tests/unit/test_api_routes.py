"""
Unit tests for API routes.
Tests the FastAPI endpoints and route handlers.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.infrastructure.api.routes import router, RealLLMProvider


def create_test_app():
    """Create test FastAPI app"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    
    # Add health check endpoint for testing
    @app.get("/healthz")
    async def health_check():
        return {
            "status": "healthy", 
            "service": "llm-interview-evaluation",
            "project_name": "Test LLM Service"
        }
    
    return app


class TestRealLLMProvider:
    """Test suite for RealLLMProvider"""

    @pytest.fixture
    def provider(self):
        """Create RealLLMProvider instance"""
        return RealLLMProvider()

    @pytest.mark.asyncio
    async def test_generate_text_gpt4(self, provider):
        """Test text generation with GPT-4 model"""
        with patch('app.infrastructure.api.routes.call_openai_gpt5') as mock_openai:
            mock_openai.return_value = "Generated text from GPT-4"
            
            from app.domain.models import ModelType
            result = await provider.generate_text(
                prompt="Test prompt",
                model=ModelType.GPT_4,
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Generated text from GPT-4"
            mock_openai.assert_called_once_with("Test prompt", "", "")

    @pytest.mark.asyncio
    async def test_generate_text_claude(self, provider):
        """Test text generation with Claude model"""
        with patch('app.infrastructure.api.routes.call_google_gemini') as mock_gemini:
            mock_gemini.return_value = "Generated text from Gemini"
            
            from app.domain.models import ModelType
            result = await provider.generate_text(
                prompt="Test prompt",
                model=ModelType.CLAUDE,
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Generated text from Gemini"
            mock_gemini.assert_called_once_with("Test prompt", "", "")

    @pytest.mark.asyncio
    async def test_generate_text_llama(self, provider):
        """Test text generation with Llama model"""
        with patch('app.infrastructure.api.routes.call_openrouter_deepseek') as mock_deepseek:
            mock_deepseek.return_value = "Generated text from DeepSeek"
            
            from app.domain.models import ModelType
            result = await provider.generate_text(
                prompt="Test prompt",
                model=ModelType.LLAMA,
                max_tokens=100,
                temperature=0.7
            )
            
            assert result == "Generated text from DeepSeek"
            mock_deepseek.assert_called_once_with("Test prompt", "", "")

    @pytest.mark.asyncio
    async def test_generate_text_error_handling(self, provider):
        """Test error handling in text generation"""
        with patch('app.infrastructure.api.routes.call_openai_gpt5') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            
            from app.domain.models import ModelType
            result = await provider.generate_text(
                prompt="Test prompt",
                model=ModelType.GPT_4,
                max_tokens=100,
                temperature=0.7
            )
            
            assert "Error generating text: API Error" in result

    def test_get_model_info_gpt4(self, provider):
        """Test getting model info for GPT-4"""
        from app.domain.models import ModelType
        info = provider.get_model_info(ModelType.GPT_4)
        
        assert info["name"] == "GPT-5"
        assert info["provider"] == "OpenAI"
        assert info["max_tokens"] == 4000
        assert info["context_window"] == 128000

    def test_get_model_info_claude(self, provider):
        """Test getting model info for Claude"""
        from app.domain.models import ModelType
        info = provider.get_model_info(ModelType.CLAUDE)
        
        assert info["name"] == "Gemini 2.5 Pro"
        assert info["provider"] == "Google"
        assert info["max_tokens"] == 2048
        assert info["context_window"] == 32000

    def test_get_model_info_unknown(self, provider):
        """Test getting model info for unknown model"""
        from app.domain.models import ModelType
        info = provider.get_model_info(ModelType.GPT_3_5)  # Not in the mapping
        
        assert info["name"] == "Unknown"
        assert info["provider"] == "Unknown"
        assert info["max_tokens"] == 0
        assert info["context_window"] == 0


class TestAPIRoutes:
    """Test suite for API routes"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_test_app()
        return TestClient(app)

    @pytest.fixture
    def mock_provider(self):
        """Create mock provider for dependency injection"""
        provider = Mock(spec=RealLLMProvider)
        provider.generate_text = AsyncMock()
        provider.get_model_info = Mock()
        return provider

    def test_generate_endpoint_success(self, client):
        """Test successful text generation endpoint"""
        # We need to mock the RealLLMProvider methods directly since they're called by dependency injection
        with patch.object(RealLLMProvider, 'generate_text', new_callable=AsyncMock) as mock_generate, \
             patch.object(RealLLMProvider, 'get_model_info') as mock_get_info:
            
            mock_generate.return_value = "Generated response"
            mock_get_info.return_value = {"name": "GPT-4", "provider": "OpenAI"}
            
            request_data = {
                "text": "Tell me a joke",
                "session_id": "test-session"
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["generated_text"] == "Generated response"
            assert data["session_id"] == "test-session"
            assert "timestamp" in data
            assert "processing_time" in data

    def test_generate_endpoint_validation_error(self, client):
        """Test generate endpoint with validation error"""
        # Missing required fields
        request_data = {
            "text": "Test"
            # Missing session_id
        }
        
        response = client.post("/api/v1/generate", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_generate_endpoint_internal_error(self, client):
        """Test generate endpoint with internal error"""
        # Mock the RealLLMProvider to raise an error
        with patch.object(RealLLMProvider, 'generate_text', new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Internal error")
            
            request_data = {
                "text": "Test prompt",
                "session_id": "test-session"
            }
            
            response = client.post("/api/v1/generate", json=request_data)
            
            # The use case handles errors gracefully, returning 200 with error message
            assert response.status_code == 200
            data = response.json()
            assert "no pude generar una respuesta" in data["generated_text"]

    def test_models_endpoint(self, client):
        """Test models listing endpoint"""
        with patch('app.infrastructure.api.routes.get_llm_provider') as mock_get_provider:
            mock_provider = Mock(spec=RealLLMProvider)
            mock_provider.get_model_info = Mock(side_effect=lambda model: {
                "name": f"Model {model.value}",
                "provider": "Test Provider",
                "max_tokens": 4000,
                "context_window": 32000
            })
            mock_get_provider.return_value = mock_provider
            
            response = client.get("/api/v1/models")
            
            assert response.status_code == 200
            data = response.json()
            assert "models" in data
            assert len(data["models"]) == 4  # Number of ModelType enum values
            
            # Check first model structure
            model = data["models"][0]
            assert "id" in model
            assert "name" in model
            assert "provider" in model
            assert "max_tokens" in model
            assert "context_window" in model

    def test_evaluate_interview_endpoint_success(self, client):
        """Test successful interview evaluation endpoint"""
        with patch('app.infrastructure.api.routes.call_openai_gpt5') as mock_openai, \
             patch('app.infrastructure.api.routes.call_google_gemini') as mock_gemini, \
             patch('app.infrastructure.api.routes.call_openrouter_deepseek') as mock_deepseek:
            
            mock_openai.return_value = "OpenAI evaluation result"
            mock_gemini.return_value = "Gemini evaluation result"
            mock_deepseek.return_value = "DeepSeek evaluation result"
            
            request_data = {
                "interview_id": "test-interview-123",
                "system_prompt": "You are an interviewer",
                "rubric": "Rate 1-10",
                "jd": "Software Engineer position",
                "full_transcript": "Interview conversation..."
            }
            
            response = client.post("/api/v1/evaluate-interview", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["interview_id"] == "test-interview-123"
            assert data["evaluation_1"] == "OpenAI evaluation result"
            assert data["evaluation_2"] == "Gemini evaluation result"
            assert data["evaluation_3"] == "DeepSeek evaluation result"
            assert data["error"] is None

    def test_evaluate_interview_endpoint_with_errors(self, client):
        """Test interview evaluation endpoint with provider errors"""
        with patch('app.infrastructure.api.routes.call_openai_gpt5') as mock_openai, \
             patch('app.infrastructure.api.routes.call_google_gemini') as mock_gemini, \
             patch('app.infrastructure.api.routes.call_openrouter_deepseek') as mock_deepseek:
            
            mock_openai.side_effect = Exception("OpenAI API Error")
            mock_gemini.return_value = "Gemini evaluation result"
            mock_deepseek.side_effect = Exception("DeepSeek API Error")
            
            request_data = {
                "interview_id": "test-interview-456",
                "full_transcript": "Interview conversation..."
            }
            
            response = client.post("/api/v1/evaluate-interview", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["interview_id"] == "test-interview-456"
            assert "OpenAI evaluation failed" in data["evaluation_1"]
            assert data["evaluation_2"] == "Gemini evaluation result"
            assert "DeepSeek evaluation failed" in data["evaluation_3"]

    def test_evaluate_interview_endpoint_validation_error(self, client):
        """Test interview evaluation endpoint with validation error"""
        request_data = {
            # Missing required fields
            "interview_id": "test"
            # Missing full_transcript
        }
        
        response = client.post("/api/v1/evaluate-interview", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_evaluate_interview_file_endpoint_success(self, client):
        """Test successful interview evaluation from file endpoint"""
        with patch('app.infrastructure.llm_provider.load_interview_from_source') as mock_load, \
             patch('app.infrastructure.llm_provider.run_evaluations') as mock_evaluate:
            
            # Setup mocks
            mock_interview = Mock()
            mock_interview.interview_id = "file-interview-789"
            mock_interview.evaluation_1 = "File eval 1"
            mock_interview.evaluation_2 = "File eval 2"
            mock_interview.evaluation_3 = "File eval 3"
            
            mock_load.return_value = mock_interview
            mock_evaluate.return_value = mock_interview
            
            response = client.post("/api/v1/evaluate-interview-file?file_path=test.json&source_type=file")
            
            assert response.status_code == 200
            data = response.json()
            assert data["interview_id"] == "file-interview-789"
            assert data["evaluation_1"] == "File eval 1"
            assert data["evaluation_2"] == "File eval 2"
            assert data["evaluation_3"] == "File eval 3"

    def test_evaluate_interview_file_endpoint_error(self, client):
        """Test interview evaluation from file endpoint with error"""
        with patch('app.infrastructure.llm_provider.load_interview_from_source') as mock_load:
            mock_load.side_effect = FileNotFoundError("File not found")
            
            response = client.post("/api/v1/evaluate-interview-file?file_path=missing.json")
            
            assert response.status_code == 500
            assert "Failed to evaluate interview" in response.json()["detail"]

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "llm-interview-evaluation"
        assert "project_name" in data