"""
API routes for reporting and analytics on interview evaluations.
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io
import json

from ...domain.entities.interview import Interview
from ...infrastructure.config import get_settings
from ...infrastructure.persistence.supabase.interview_repository import InterviewRepository
from ..api.models import (
    InterviewResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1", tags=["reporting"])

# Dependency to get repository
def get_interview_repository():
    return InterviewRepository()


@router.get("/reports/summary")
async def get_evaluation_summary(
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get summary statistics of all evaluations"""
    try:
        # Get all interviews
        all_interviews = await repository.list_all(limit=1000)  # Adjust limit as needed
        
        total_interviews = len(all_interviews)
        evaluated_interviews = [i for i in all_interviews if any([i.evaluation_1, i.evaluation_2, i.evaluation_3])]
        fully_evaluated = [i for i in all_interviews if all([i.evaluation_1, i.evaluation_2, i.evaluation_3])]
        
        # Provider-specific stats
        openai_completed = len([i for i in all_interviews if i.evaluation_1])
        gemini_completed = len([i for i in all_interviews if i.evaluation_2])
        deepseek_completed = len([i for i in all_interviews if i.evaluation_3])
        
        return {
            "summary": {
                "total_interviews": total_interviews,
                "evaluated_interviews": len(evaluated_interviews),
                "fully_evaluated_interviews": len(fully_evaluated),
                "evaluation_completion_rate": len(evaluated_interviews) / total_interviews if total_interviews > 0 else 0,
                "full_completion_rate": len(fully_evaluated) / total_interviews if total_interviews > 0 else 0
            },
            "provider_statistics": {
                "openai_gpt5": {
                    "completed": openai_completed,
                    "completion_rate": openai_completed / total_interviews if total_interviews > 0 else 0
                },
                "google_gemini": {
                    "completed": gemini_completed,
                    "completion_rate": gemini_completed / total_interviews if total_interviews > 0 else 0
                },
                "deepseek": {
                    "completed": deepseek_completed,
                    "completion_rate": deepseek_completed / total_interviews if total_interviews > 0 else 0
                }
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/reports/interviews/evaluated")
async def get_evaluated_interviews(
    provider: Optional[str] = None,
    limit: int = 50,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get list of interviews that have been evaluated, optionally filtered by provider"""
    try:
        evaluated_interviews = await repository.get_by_status(has_evaluations=True)
        
        # Filter by provider if specified
        if provider:
            if provider.lower() == "openai":
                evaluated_interviews = [i for i in evaluated_interviews if i.evaluation_1]
            elif provider.lower() == "gemini":
                evaluated_interviews = [i for i in evaluated_interviews if i.evaluation_2]
            elif provider.lower() == "deepseek":
                evaluated_interviews = [i for i in evaluated_interviews if i.evaluation_3]
            else:
                raise HTTPException(status_code=400, detail="Invalid provider. Use: openai, gemini, or deepseek")
        
        # Apply limit
        evaluated_interviews = evaluated_interviews[:limit]
        
        # Convert to response format
        from .routes import interview_to_response
        interview_responses = [interview_to_response(interview) for interview in evaluated_interviews]
        
        return {
            "interviews": interview_responses,
            "total": len(interview_responses),
            "filter": {"provider": provider} if provider else None,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evaluated interviews: {str(e)}")


@router.get("/reports/interviews/pending")
async def get_pending_interviews(
    limit: int = 50,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get list of interviews that are pending evaluation"""
    try:
        pending_interviews = await repository.get_by_status(has_evaluations=False)
        
        # Apply limit
        pending_interviews = pending_interviews[:limit]
        
        # Convert to response format
        from .routes import interview_to_response
        interview_responses = [interview_to_response(interview) for interview in pending_interviews]
        
        return {
            "interviews": interview_responses,
            "total": len(interview_responses),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending interviews: {str(e)}")


@router.get("/reports/interview/{interview_id}")
async def get_interview_report(
    interview_id: str,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get detailed report for a specific interview"""
    try:
        interview = await repository.get_by_id(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Analyze evaluations
        evaluations = {
            "openai_gpt5": {
                "content": interview.evaluation_1,
                "completed": interview.evaluation_1 is not None,
                "length": len(interview.evaluation_1) if interview.evaluation_1 else 0
            },
            "google_gemini": {
                "content": interview.evaluation_2,
                "completed": interview.evaluation_2 is not None,
                "length": len(interview.evaluation_2) if interview.evaluation_2 else 0
            },
            "deepseek": {
                "content": interview.evaluation_3,
                "completed": interview.evaluation_3 is not None,
                "length": len(interview.evaluation_3) if interview.evaluation_3 else 0
            }
        }
        
        # Basic analysis
        total_evaluations = sum(1 for eval in evaluations.values() if eval["completed"])
        avg_length = sum(eval["length"] for eval in evaluations.values()) / max(total_evaluations, 1)
        
        return {
            "interview_id": interview_id,
            "basic_info": {
                "has_job_description": bool(interview.jd),
                "has_transcript": bool(interview.full_transcript),
                "has_system_prompt": bool(interview.system_prompt),
                "has_rubric": bool(interview.rubric),
                "transcript_length": len(interview.full_transcript) if interview.full_transcript else 0
            },
            "evaluation_status": {
                "total_completed": total_evaluations,
                "completion_percentage": (total_evaluations / 3) * 100,
                "average_evaluation_length": avg_length
            },
            "evaluations": evaluations,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate interview report: {str(e)}")


@router.get("/reports/export/json")
async def export_interviews_json(
    include_evaluations: bool = True,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Export all interviews as JSON"""
    try:
        all_interviews = await repository.list_all(limit=1000)  # Adjust as needed
        
        export_data = []
        for interview in all_interviews:
            interview_data = {
                "interview_id": interview.interview_id,
                "system_prompt": interview.system_prompt,
                "rubric": interview.rubric,
                "jd": interview.jd,
                "full_transcript": interview.full_transcript,
            }
            
            if include_evaluations:
                interview_data.update({
                    "evaluation_1": interview.evaluation_1,
                    "evaluation_2": interview.evaluation_2,
                    "evaluation_3": interview.evaluation_3,
                })
            
            export_data.append(interview_data)
        
        # Create JSON response
        json_content = json.dumps({
            "export_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_interviews": len(export_data),
                "includes_evaluations": include_evaluations
            },
            "interviews": export_data
        }, indent=2)
        
        # Return as downloadable file
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=interviews_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export interviews: {str(e)}")


@router.get("/reports/analytics/evaluation-lengths")
async def get_evaluation_length_analytics(
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Get analytics on evaluation lengths by provider"""
    try:
        evaluated_interviews = await repository.get_by_status(has_evaluations=True)
        
        openai_lengths = [len(i.evaluation_1) for i in evaluated_interviews if i.evaluation_1]
        gemini_lengths = [len(i.evaluation_2) for i in evaluated_interviews if i.evaluation_2]
        deepseek_lengths = [len(i.evaluation_3) for i in evaluated_interviews if i.evaluation_3]
        
        def calculate_stats(lengths):
            if not lengths:
                return {"count": 0, "avg": 0, "min": 0, "max": 0}
            return {
                "count": len(lengths),
                "avg": sum(lengths) / len(lengths),
                "min": min(lengths),
                "max": max(lengths)
            }
        
        return {
            "provider_analytics": {
                "openai_gpt5": calculate_stats(openai_lengths),
                "google_gemini": calculate_stats(gemini_lengths),
                "deepseek": calculate_stats(deepseek_lengths)
            },
            "overall_statistics": {
                "total_evaluations": len(openai_lengths) + len(gemini_lengths) + len(deepseek_lengths),
                "interviews_analyzed": len(evaluated_interviews)
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")


@router.post("/reports/compare/{interview_id}")
async def compare_evaluations(
    interview_id: str,
    repository: InterviewRepository = Depends(get_interview_repository)
):
    """Compare evaluations from different providers for an interview"""
    try:
        interview = await repository.get_by_id(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        evaluations = []
        if interview.evaluation_1:
            evaluations.append({"provider": "OpenAI GPT-5", "content": interview.evaluation_1})
        if interview.evaluation_2:
            evaluations.append({"provider": "Google Gemini", "content": interview.evaluation_2})
        if interview.evaluation_3:
            evaluations.append({"provider": "DeepSeek", "content": interview.evaluation_3})
        
        if len(evaluations) < 2:
            raise HTTPException(status_code=400, detail="At least 2 evaluations needed for comparison")
        
        # Basic comparison metrics
        lengths = [len(eval["content"]) for eval in evaluations]
        length_variance = max(lengths) - min(lengths)
        
        return {
            "interview_id": interview_id,
            "comparison_metrics": {
                "total_evaluations": len(evaluations),
                "length_variance": length_variance,
                "average_length": sum(lengths) / len(lengths),
                "shortest_evaluation": min(lengths),
                "longest_evaluation": max(lengths)
            },
            "evaluations": evaluations,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare evaluations: {str(e)}")