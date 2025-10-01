"""
Unit tests for Interview domain entity.
Tests the Interview class functionality including serialization.
"""
import pytest
from app.domain.entities.interview import Interview


class TestInterview:
    """Test suite for Interview domain entity"""

    def test_interview_creation_with_defaults(self):
        """Test creating Interview with default values"""
        interview = Interview()
        
        assert interview.interview_id is None
        assert "expert technical recruiter" in interview.system_prompt
        assert "Evaluation Rubric" in interview.rubric
        assert "Senior Software Engineer" in interview.jd
        assert "challenging project" in interview.full_transcript
        assert interview.evaluation_1 is None
        assert interview.evaluation_2 is None
        assert interview.evaluation_3 is None

    def test_interview_creation_with_custom_values(self):
        """Test creating Interview with custom values"""
        interview = Interview(
            interview_id="custom-123",
            system_prompt="Custom prompt",
            rubric="Custom rubric",
            jd="Custom job description",
            full_transcript="Custom transcript"
        )
        
        assert interview.interview_id == "custom-123"
        assert interview.system_prompt == "Custom prompt"
        assert interview.rubric == "Custom rubric"
        assert interview.jd == "Custom job description"
        assert interview.full_transcript == "Custom transcript"

    def test_interview_creation_partial_custom(self):
        """Test creating Interview with some custom values"""
        interview = Interview(
            interview_id="partial-456",
            system_prompt="Custom prompt only"
        )
        
        assert interview.interview_id == "partial-456"
        assert interview.system_prompt == "Custom prompt only"
        # Other fields should use defaults
        assert "Evaluation Rubric" in interview.rubric
        assert "Senior Software Engineer" in interview.jd

    def test_interview_to_dict(self):
        """Test Interview serialization to dictionary"""
        interview = Interview(
            interview_id="test-789",
            system_prompt="Test prompt",
            rubric="Test rubric",
            jd="Test JD",
            full_transcript="Test transcript"
        )
        interview.evaluation_1 = "First evaluation"
        interview.evaluation_2 = "Second evaluation"
        
        result = interview.to_dict()
        
        assert isinstance(result, dict)
        assert result['interview_id'] == "test-789"
        assert result['system_prompt'] == "Test prompt"
        assert result['rubric'] == "Test rubric"
        assert result['jd'] == "Test JD"
        assert result['full_transcript'] == "Test transcript"
        assert result['evaluation_1'] == "First evaluation"
        assert result['evaluation_2'] == "Second evaluation"
        assert result['evaluation_3'] is None

    def test_interview_from_dict(self):
        """Test Interview deserialization from dictionary"""
        data = {
            'interview_id': 'dict-123',
            'system_prompt': 'Dict prompt',
            'rubric': 'Dict rubric',
            'jd': 'Dict JD',
            'full_transcript': 'Dict transcript',
            'evaluation_1': 'Dict eval 1',
            'evaluation_2': 'Dict eval 2',
            'evaluation_3': 'Dict eval 3'
        }
        
        interview = Interview.from_dict(data)
        
        assert interview.interview_id == 'dict-123'
        assert interview.system_prompt == 'Dict prompt'
        assert interview.rubric == 'Dict rubric'
        assert interview.jd == 'Dict JD'
        assert interview.full_transcript == 'Dict transcript'
        assert interview.evaluation_1 == 'Dict eval 1'
        assert interview.evaluation_2 == 'Dict eval 2'
        assert interview.evaluation_3 == 'Dict eval 3'

    def test_interview_from_dict_partial(self):
        """Test Interview deserialization from partial dictionary"""
        data = {
            'interview_id': 'partial-dict-456',
            'system_prompt': 'Partial prompt',
            'evaluation_1': 'Only first evaluation'
        }
        
        interview = Interview.from_dict(data)
        
        assert interview.interview_id == 'partial-dict-456'
        assert interview.system_prompt == 'Partial prompt'
        assert interview.evaluation_1 == 'Only first evaluation'
        # Missing fields should be None or use defaults
        assert interview.rubric is None or "Evaluation Rubric" in interview.rubric
        assert interview.evaluation_2 is None
        assert interview.evaluation_3 is None

    def test_interview_from_dict_empty(self):
        """Test Interview deserialization from empty dictionary"""
        data = {}
        
        interview = Interview.from_dict(data)
        
        # Should create interview with defaults since no data provided
        assert interview.interview_id is None
        assert interview.evaluation_1 is None
        assert interview.evaluation_2 is None
        assert interview.evaluation_3 is None

    def test_interview_round_trip_serialization(self):
        """Test Interview round-trip serialization (to_dict -> from_dict)"""
        original = Interview(
            interview_id="roundtrip-789",
            system_prompt="Original prompt",
            rubric="Original rubric",
            jd="Original JD",
            full_transcript="Original transcript"
        )
        original.evaluation_1 = "Original eval 1"
        original.evaluation_2 = "Original eval 2"
        original.evaluation_3 = "Original eval 3"
        
        # Serialize to dict
        data = original.to_dict()
        
        # Deserialize back to object
        reconstructed = Interview.from_dict(data)
        
        # Compare all fields
        assert reconstructed.interview_id == original.interview_id
        assert reconstructed.system_prompt == original.system_prompt
        assert reconstructed.rubric == original.rubric
        assert reconstructed.jd == original.jd
        assert reconstructed.full_transcript == original.full_transcript
        assert reconstructed.evaluation_1 == original.evaluation_1
        assert reconstructed.evaluation_2 == original.evaluation_2
        assert reconstructed.evaluation_3 == original.evaluation_3

    def test_interview_repr(self):
        """Test Interview string representation"""
        interview = Interview(interview_id="repr-test")
        interview.evaluation_1 = "Has evaluation"
        
        repr_str = repr(interview)
        
        assert "repr-test" in repr_str
        assert "eval_1_populated=True" in repr_str
        assert "eval_2_populated=False" in repr_str
        assert "eval_3_populated=False" in repr_str

    def test_interview_default_methods(self):
        """Test Interview default value methods"""
        interview = Interview()
        
        # Test that default methods are accessible
        default_prompt = interview._default_system_prompt()
        default_rubric = interview._default_rubric()
        default_jd = interview._default_jd()
        default_transcript = interview._default_full_transcript()
        
        assert isinstance(default_prompt, str)
        assert len(default_prompt) > 0
        assert isinstance(default_rubric, str)
        assert len(default_rubric) > 0
        assert isinstance(default_jd, str)
        assert len(default_jd) > 0
        assert isinstance(default_transcript, str)
        assert len(default_transcript) > 0

    def test_interview_evaluation_population(self):
        """Test Interview evaluation field population"""
        interview = Interview(interview_id="eval-test")
        
        # Initially all evaluations should be None
        assert interview.evaluation_1 is None
        assert interview.evaluation_2 is None
        assert interview.evaluation_3 is None
        
        # Populate evaluations
        interview.evaluation_1 = "First LLM evaluation"
        interview.evaluation_2 = "Second LLM evaluation"
        interview.evaluation_3 = "Third LLM evaluation"
        
        # Verify evaluations are set
        assert interview.evaluation_1 == "First LLM evaluation"
        assert interview.evaluation_2 == "Second LLM evaluation"
        assert interview.evaluation_3 == "Third LLM evaluation"

    def test_interview_none_values_handling(self):
        """Test Interview handling of None values"""
        interview = Interview(
            interview_id=None,
            system_prompt=None,
            rubric=None,
            jd=None,
            full_transcript=None
        )
        
        # None values should trigger defaults
        assert interview.interview_id is None  # This one stays None
        assert interview.system_prompt is not None  # Should use default
        assert interview.rubric is not None  # Should use default
        assert interview.jd is not None  # Should use default
        assert interview.full_transcript is not None  # Should use default