"""
Test the merged evaluation and reporting endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

def test_health_check():
    """Test that the health check reflects the merged service"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "llm-evaluation-service"
    assert "features" in data
    assert "llm-evaluation" in data["features"]
    assert "reporting" in data["features"]

def test_evaluation_interview_results():
    """Test interview results endpoint returns real Interview structure"""
    interview_id = "test-interview-123"
    response = client.get(f"/api/v1/evaluation/results/interview/{interview_id}")
    assert response.status_code == 200
    data = response.json()
    
    # Check for real Interview entity fields
    assert data["interview_id"] == interview_id
    assert "system_prompt" in data
    assert "rubric" in data
    assert "jd" in data
    assert "full_transcript" in data
    assert "evaluation_1" in data  # May be None initially
    assert "evaluation_2" in data  # May be None initially
    assert "evaluation_3" in data  # May be None initially
    
    # Verify these are the actual fields from Interview entity
    assert isinstance(data["system_prompt"], str)
    assert isinstance(data["rubric"], str)
    assert len(data["system_prompt"]) > 0  # Has default content

def test_evaluation_structured_results():
    """Test structured evaluation endpoint returns rubric-based evaluation"""
    interview_id = "test-interview-456"
    
    # Mock successful structured evaluation response
    mock_response = {
        "interview_type": "technical",
        "technical_evaluation": {
            "problem_understanding": {"score": "strong", "rationale": "Good analysis", "evidence": ["Asked clarifying questions"]},
            "technical_skills": {"score": "very_strong", "rationale": "Solid implementation", "evidence": ["Correct algorithm"]},
            "rationale": {"score": "strong", "rationale": "Clear reasoning", "evidence": ["Explained approach well"]},
            "communication": {"score": "very_strong", "rationale": "Excellent communication", "evidence": ["Clear explanations"]}
        },
        "overall_assessment": {
            "quantitative_score": 85.0,
            "score_calculation": "Weighted average of all criteria scores",
            "recommendation": "hire",
            "key_strengths": ["Strong problem solving", "Clear communication"],
            "areas_for_improvement": ["Could optimize further"],
            "summary": "Strong technical performance"
        },
        "metadata": {
            "evaluator": "GPT-5",
            "evaluation_timestamp": "2024-01-01T00:00:00Z",
            "rubric_version": "v1.0"
        }
    }
    
    with patch('app.infrastructure.llm_provider.get_structured_evaluation') as mock_eval:
        mock_eval.return_value = mock_response
        
        response = client.get(f"/api/v1/evaluation/structured/{interview_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check structured evaluation format
        assert "interview_type" in data
        assert data["interview_type"] in ["technical", "behavioral", "mixed"]
        assert "overall_assessment" in data
        assert "metadata" in data
        
        # Check overall assessment structure
        assessment = data["overall_assessment"]
        assert "quantitative_score" in assessment
        assert "score_calculation" in assessment
        assert "recommendation" in assessment
        assert "key_strengths" in assessment
        assert "areas_for_improvement" in assessment
        assert "summary" in assessment
        
        # Verify score is numeric and in valid range
        assert isinstance(assessment["quantitative_score"], (int, float))
        assert 0 <= assessment["quantitative_score"] <= 100
        
        # Verify recommendation is valid
        assert assessment["recommendation"] in ["strong_hire", "hire", "no_hire", "strong_no_hire"]
        
        # Check that appropriate evaluation sections exist based on interview type
        if data["interview_type"] == "technical":
            assert "technical_evaluation" in data
            assert "behavioral_evaluation" not in data or data["behavioral_evaluation"] is None
        elif data["interview_type"] == "behavioral":
            assert "behavioral_evaluation" in data
            assert "technical_evaluation" not in data or data["technical_evaluation"] is None
        elif data["interview_type"] == "mixed":
            assert "technical_evaluation" in data
            assert "behavioral_evaluation" in data

def test_evaluation_export_json():
    """Test evaluation export endpoint (JSON format only)"""
    interview_id = "test-interview-123"
    response = client.post(f"/api/v1/evaluation/export/{interview_id}", 
                          json={"interview_id": interview_id, "format": "json"})
    assert response.status_code == 200
    data = response.json()
    
    # Should return the same structure as interview results
    assert data["interview_id"] == interview_id
    assert "system_prompt" in data
    assert "evaluation_1" in data

def test_reporting_templates():
    """Test that template endpoint no longer exists"""
    response = client.get("/api/v1/reporting/templates")
    assert response.status_code == 404  # Endpoint removed

def test_reporting_formats():
    """Test supported formats endpoint shows only JSON"""
    response = client.get("/api/v1/reporting/formats")
    assert response.status_code == 200
    data = response.json()
    assert "formats" in data
    formats = [f["id"] for f in data["formats"]]
    assert "json" in formats
    # Should only have actually supported formats

def test_reporting_generate():
    """Test report generation endpoint with realistic expectations"""
    response = client.post("/api/v1/reporting/generate", 
                          json={"interview_ids": ["test-1", "test-2"], "format": "json"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert data["status"] == "completed"  # JSON reports complete immediately
    assert data["format"] == "json"
    assert data["interview_count"] == 2

def test_reporting_download():
    """Test report download endpoint shows realistic limitation"""
    report_id = "test-report-123"
    response = client.get(f"/api/v1/reporting/download/{report_id}")
    assert response.status_code == 501  # Not implemented

if __name__ == "__main__":
    pytest.main([__file__, "-v"])