"""
Integration tests for LLM service.
Tests the full service integration with real components.
"""
import pytest
import json
import tempfile
import os
from unittest.mock import patch
from app.infrastructure.llm_provider import (
    load_interview_from_source,
    run_evaluations
)
from app.domain.entities.interview import Interview


class TestLLMServiceIntegration:
    """Integration test suite for LLM service"""

    @pytest.fixture
    def sample_interview_data(self):
        """Sample interview data for testing"""
        return {
            "interview_id": "integration-test-123",
            "system_prompt": "You are an expert technical recruiter.",
            "rubric": "Rate technical skills (1-10), communication (1-10), culture fit (1-10).",
            "jd": "Senior Python Developer with 5+ years experience.",
            "full_transcript": "Interviewer: Tell me about your Python experience. Candidate: I have 6 years of Python development experience..."
        }

    @pytest.fixture
    def temp_interview_file(self, sample_interview_data):
        """Create temporary interview file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_interview_data, f)
            temp_file_path = f.name
        
        yield temp_file_path
        
        # Cleanup
        os.unlink(temp_file_path)

    def test_load_interview_from_file_integration(self, temp_interview_file, sample_interview_data):
        """Test loading interview from file (integration)"""
        interview = load_interview_from_source('file', temp_interview_file)
        
        assert isinstance(interview, Interview)
        assert interview.interview_id == sample_interview_data["interview_id"]
        assert interview.system_prompt == sample_interview_data["system_prompt"]
        assert interview.rubric == sample_interview_data["rubric"]
        assert interview.jd == sample_interview_data["jd"]
        assert interview.full_transcript == sample_interview_data["full_transcript"]

    def test_interview_serialization_integration(self, sample_interview_data):
        """Test Interview serialization/deserialization integration"""
        # Create interview from dict
        original_interview = Interview.from_dict(sample_interview_data)
        
        # Add some evaluations
        original_interview.evaluation_1 = "Strong technical skills"
        original_interview.evaluation_2 = "Good communication"
        original_interview.evaluation_3 = "Culture fit looks good"
        
        # Serialize to dict
        serialized = original_interview.to_dict()
        
        # Deserialize back
        restored_interview = Interview.from_dict(serialized)
        
        # Verify all fields match
        assert restored_interview.interview_id == original_interview.interview_id
        assert restored_interview.system_prompt == original_interview.system_prompt
        assert restored_interview.rubric == original_interview.rubric
        assert restored_interview.jd == original_interview.jd
        assert restored_interview.full_transcript == original_interview.full_transcript
        assert restored_interview.evaluation_1 == original_interview.evaluation_1
        assert restored_interview.evaluation_2 == original_interview.evaluation_2
        assert restored_interview.evaluation_3 == original_interview.evaluation_3

    def test_file_to_evaluation_workflow_integration(self, temp_interview_file):
        """Test complete workflow: file -> interview -> evaluation"""
        with patch('app.infrastructure.llm_provider.call_openai_gpt5') as mock_openai, \
             patch('app.infrastructure.llm_provider.call_google_gemini') as mock_gemini, \
             patch('app.infrastructure.llm_provider.call_openrouter_deepseek') as mock_deepseek:
            
            # Setup mocks
            mock_openai.return_value = "OpenAI: Candidate shows strong Python skills and experience."
            mock_gemini.return_value = "Gemini: Good technical background, clear communication."
            mock_deepseek.return_value = "DeepSeek: Solid candidate with relevant experience."
            
            # Load interview from file
            interview = load_interview_from_source('file', temp_interview_file)
            
            # Run evaluations
            evaluated_interview = run_evaluations(interview)
            
            # Verify evaluations were populated
            assert evaluated_interview.evaluation_1 == "OpenAI: Candidate shows strong Python skills and experience."
            assert evaluated_interview.evaluation_2 == "Gemini: Good technical background, clear communication."
            assert evaluated_interview.evaluation_3 == "DeepSeek: Solid candidate with relevant experience."
            
            # Verify original interview data is preserved
            assert evaluated_interview.interview_id == "integration-test-123"
            assert "technical recruiter" in evaluated_interview.system_prompt
            assert "Python Developer" in evaluated_interview.jd

    def test_interview_defaults_integration(self):
        """Test Interview creation with defaults integration"""
        interview = Interview(interview_id="defaults-test")
        
        # Verify defaults are set
        assert interview.interview_id == "defaults-test"
        assert len(interview.system_prompt) > 0
        assert "technical recruiter" in interview.system_prompt.lower()
        assert len(interview.rubric) > 0
        assert "technical proficiency" in interview.rubric.lower()
        assert len(interview.jd) > 0
        assert "software engineer" in interview.jd.lower()
        assert len(interview.full_transcript) > 0
        assert "interviewer" in interview.full_transcript.lower()
        
        # Verify evaluations are initially None
        assert interview.evaluation_1 is None
        assert interview.evaluation_2 is None
        assert interview.evaluation_3 is None

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios"""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            load_interview_from_source('file', 'non_existent_file.json')
        
        # Test with unsupported source type
        with pytest.raises(ValueError, match="Unsupported source type"):
            load_interview_from_source('unsupported_type', 'some_identifier')

    def test_evaluation_error_handling_integration(self):
        """Test evaluation error handling integration"""
        interview = Interview(interview_id="error-test")
        
        with patch('app.infrastructure.llm_provider.call_openai_gpt5') as mock_openai, \
             patch('app.infrastructure.llm_provider.call_google_gemini') as mock_gemini, \
             patch('app.infrastructure.llm_provider.call_openrouter_deepseek') as mock_deepseek:
            
            # Setup one success and two failures
            mock_openai.return_value = "Successful evaluation"
            mock_gemini.side_effect = Exception("Gemini API Error")
            mock_deepseek.side_effect = Exception("DeepSeek API Error")
            
            # Run evaluations - should not raise exceptions
            evaluated_interview = run_evaluations(interview)
            
            # Verify successful evaluation was captured
            assert evaluated_interview.evaluation_1 == "Successful evaluation"
            
            # Note: The current implementation doesn't handle individual LLM errors
            # This test documents the current behavior
            assert evaluated_interview.interview_id == "error-test"

    def test_malformed_json_handling_integration(self):
        """Test handling of malformed JSON files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content }")
            temp_file = f.name
        
        try:
            with pytest.raises(Exception):  # JSON decode error
                load_interview_from_source('file', temp_file)
        finally:
            os.unlink(temp_file)

    def test_empty_json_file_integration(self):
        """Test handling of empty JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_file = f.name
        
        try:
            interview = load_interview_from_source('file', temp_file)
            
            # Should create interview with defaults since no data provided
            assert interview.interview_id is None
            assert len(interview.system_prompt) > 0  # Should use default
            assert len(interview.rubric) > 0  # Should use default
        finally:
            os.unlink(temp_file)

    def test_partial_interview_data_integration(self):
        """Test handling of partial interview data"""
        partial_data = {
            "interview_id": "partial-test",
            "system_prompt": "Custom prompt only"
            # Missing other fields
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(partial_data, f)
            temp_file = f.name
        
        try:
            interview = load_interview_from_source('file', temp_file)
            
            # Verify provided data is preserved
            assert interview.interview_id == "partial-test"
            assert interview.system_prompt == "Custom prompt only"
            
            # Verify missing fields use defaults
            assert interview.rubric is not None
            assert interview.jd is not None
            assert interview.full_transcript is not None
        finally:
            os.unlink(temp_file)