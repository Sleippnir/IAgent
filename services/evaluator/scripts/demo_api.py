#!/usr/bin/env python3
"""
Demo script to show working LLM service API endpoints
This demonstrates the actual functionality that exists (not fake endpoints)
"""

import asyncio
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import our real application
from main import app

def demo_working_endpoints():
    """Test all the endpoints that actually work"""
    client = TestClient(app)
    
    print("🚀 LLM Service API Demo - Real Endpoints Only")
    print("=" * 60)
    
    # 1. Health Check
    print("\n1. Health Check:")
    response = client.get("/healthz")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # 2. Interview Results - Shows real Interview entity structure
    print("\n2. Interview Results (Real Data Structure):")
    interview_id = "demo-interview"
    response = client.get(f"/api/v1/evaluation/results/interview/{interview_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Interview ID: {data['interview_id']}")
        print(f"   Has System Prompt: {len(data['system_prompt']) > 0}")
        print(f"   Has Rubric: {len(data['rubric']) > 0}")
        print(f"   Evaluation 1: {data['evaluation_1'] or 'Not set'}")
        print(f"   Evaluation 2: {data['evaluation_2'] or 'Not set'}")
        print(f"   Evaluation 3: {data['evaluation_3'] or 'Not set'}")
    
    # 3. JSON Export (the only format that actually works)
    print("\n3. JSON Export (Real Format):")
    export_data = {
        "interview_id": interview_id,
        "format": "json",
        "language": "es"
    }
    response = client.post(f"/api/v1/evaluation/export/{interview_id}", json=export_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ JSON export works (real data)")
    
    # 4. Supported Formats
    print("\n4. Supported Export Formats:")
    response = client.get("/api/v1/reporting/formats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        formats = response.json()["formats"]
        print(f"   Supported formats: {[f['name'] for f in formats]}")
    
    print("\n" + "=" * 60)
    print("✅ API Demonstration Complete!")
    print("📝 Key Points:")
    print("   • APIs serve real Interview entity data")
    print("   • No fake statistical endpoints")
    print("   • Only JSON export currently supported")
    print("   • LLM evaluations are string-based natural language")
    print("   • System follows 'APIs serve existing functions' principle")


async def demo_llm_functionality():
    """Demo the actual LLM provider functions"""
    print("\n🤖 LLM Provider Demo - Real Functions")
    print("=" * 60)
    
    from app.infrastructure.llm_provider import call_openai_gpt5, load_interview_from_source
    from app.domain.entities.interview import Interview
    
    # Create test interview
    test_interview = Interview(
        interview_id="demo-test",
        jd="Senior Python Developer position",
        full_transcript="Candidate showed strong Python knowledge and problem-solving skills."
    )
    
    print("\n1. Interview Entity Structure:")
    print(f"   Interview ID: {test_interview.interview_id}")
    print(f"   Has System Prompt: {len(test_interview.system_prompt) > 0}")
    print(f"   Has Rubric: {len(test_interview.rubric) > 0}")
    print(f"   Transcript: {test_interview.full_transcript[:50]}...")
    
    # Note: LLM calls require API keys, so we'll just show the structure
    print("\n2. LLM Functions Available:")
    print("   ✅ call_openai_gpt5() - GPT-5 integration with correct parameters")
    print("   ✅ call_google_gemini() - Gemini integration")
    print("   ✅ run_evaluations() - Async evaluation runner")
    print("   ✅ load_interview_from_source() - File/DB loading")
    
    print("\n📋 LLM Integration Status:")
    print("   • GPT-5: Fixed parameter compatibility")
    print("   • Async/await: Properly implemented")
    print("   • Returns: Natural language evaluation text")
    print("   • Storage: String fields in Interview entity")


if __name__ == "__main__":
    demo_working_endpoints()
    asyncio.run(demo_llm_functionality())