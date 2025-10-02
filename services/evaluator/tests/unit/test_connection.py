#!/usr/bin/env python3
"""
Quick test to verify Supabase connection and queue operations
"""
import asyncio
from app.infrastructure.persistence.supabase.services import QueueService

async def test_connection():
    """Test Supabase connection and queue operations"""
    queue_service = QueueService()
    
    # Test auth tokens from the list
    test_tokens = [
        "19dd39d-9b6b-466a-b15f-5938bcd47152",
        "d229e635-1084-478c-bed1-40a10c66fa94",
        "eb84ea52-bfbb-4861-b431-ba2fefefc5fb"
    ]
    
    print("🔌 Testing Supabase connection...")
    
    for token in test_tokens:
        print(f"\n🔍 Testing auth token: {token}")
        try:
            interview_data = await queue_service.get_interview_from_queue(token)
            if interview_data:
                print(f"✅ Found interview for token {token}")
                print(f"📋 Data keys: {list(interview_data.keys())}")
                # Print some sample data
                for key, value in interview_data.items():
                    if isinstance(value, str) and len(value) < 100:
                        print(f"  {key}: {value}")
                    elif isinstance(value, (int, float, bool)):
                        print(f"  {key}: {value}")
                break
            else:
                print(f"❌ No interview found for token {token}")
        except Exception as e:
            print(f"💥 Error with token {token}: {str(e)}")
    
    # Test evaluator queue as well (we need an interview_id first)
    print(f"\n🔍 Testing evaluator queue with sample interview_id...")
    try:
        evaluator_data = await queue_service.get_evaluator_from_queue("sample-interview-id")
        if evaluator_data:
            print(f"✅ Found evaluator task")
            print(f"📋 Data keys: {list(evaluator_data.keys())}")
        else:
            print(f"❌ No evaluator tasks found for sample ID")
    except Exception as e:
        print(f"💥 Error getting evaluator task: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())