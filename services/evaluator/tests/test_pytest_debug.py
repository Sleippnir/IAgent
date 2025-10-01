#!/usr/bin/env python3

import pytest
import asyncio
from app.infrastructure.llm_provider import call_google_gemini, settings as llm_settings
from app.infrastructure.config import Settings

@pytest.mark.asyncio
async def test_debug_google_api():
    """Debug test to see what's happening with Google API in pytest"""
    print("\n=== DEBUG: Google API Test ===")
    
    # Check original settings
    print(f"Original llm_settings.GOOGLE_API_KEY: {llm_settings.GOOGLE_API_KEY[:15] if llm_settings.GOOGLE_API_KEY else 'None'}...")
    
    # Check new settings instance
    new_settings = Settings()
    print(f"New Settings.GOOGLE_API_KEY: {new_settings.GOOGLE_API_KEY[:15] if new_settings.GOOGLE_API_KEY else 'None'}...")
    
    # Test the call
    try:
        result = await call_google_gemini(
            "You are an expert technical interviewer evaluating a candidate's performance.",
            "Evaluate technical skills, problem-solving, and communication on a scale of 1-10.",
            "Candidate discussed Python algorithms effectively, implemented binary search correctly."
        )
        print(f"SUCCESS: Got response of length {len(result)}")
        print(f"First 100 chars: {result[:100]}")
        
        # Check for expected content
        result_lower = result.lower()
        has_content = any(word in result_lower for word in ['technical', 'python', 'experience', 'skills', 'algorithm', 'candidate'])
        print(f"Has expected content: {has_content}")
        
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise e

if __name__ == "__main__":
    import subprocess
    result = subprocess.run(['pytest', __file__ + '::test_debug_google_api', '-v', '-s'], capture_output=False)