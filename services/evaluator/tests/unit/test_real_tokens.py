#!/usr/bin/env python3
"""
Test with actual auth tokens from the database
"""
import asyncio
import json
from app.infrastructure.persistence.supabase.services import QueueService

async def test_real_tokens():
    """Test with actual auth tokens from the database"""
    queue_service = QueueService()
    
    # Test with actual auth tokens from the database
    real_tokens = [
        "675b4b3c-55d6-4efc-8610-24cb7711900b",
        "901608a4-baff-4e2f-b0f6-612427ec69ba",
        "bd52d7c1-aede-40f4-8464-4371e90f77be"
    ]
    
    print("🔌 Testing with real auth tokens from database...")
    
    for token in real_tokens:
        print(f"\n🔍 Testing auth token: {token}")
        try:
            interview_data = await queue_service.get_interview_from_queue(token)
            if interview_data:
                print(f"✅ Found interview for token {token}")
                print(f"📋 Interview ID: {interview_data.get('interview_id', 'N/A')}")
                print(f"🔗 Auth Token: {interview_data.get('auth_token', 'N/A')}")
                print(f"📅 Created: {interview_data.get('created_at', 'N/A')}")
                
                # Check payload structure
                payload = interview_data.get('payload', {})
                if payload:
                    print(f"📦 Payload keys: {list(payload.keys())}")
                    
                    # Show some sample payload data
                    if 'candidate' in payload:
                        candidate = payload['candidate']
                        print(f"👤 Candidate: {candidate.get('name', 'N/A')}")
                        
                    if 'job' in payload:
                        job = payload['job']
                        print(f"💼 Position: {job.get('title', 'N/A')}")
                        print(f"🏢 Company: {job.get('company', 'N/A')}")
                        
                    if 'transcript' in payload:
                        transcript = payload['transcript']
                        if isinstance(transcript, dict):
                            print(f"📝 Transcript keys: {list(transcript.keys())}")
                        elif isinstance(transcript, list):
                            print(f"📝 Transcript has {len(transcript)} items")
                
                # This is a good payload, let's create an Interview instance
                print(f"\n🧪 Testing Interview class with this payload...")
                try:
                    from app.domain.entities.interview import Interview
                    interview = Interview.from_json(payload)
                    print(f"✅ Successfully created Interview instance")
                    print(f"📋 Interview format ready for LLM: {len(interview.to_llm_evaluation_format())} chars")
                except Exception as e:
                    print(f"💥 Error creating Interview instance: {str(e)}")
                
                break  # Found one working example, that's enough
            else:
                print(f"❌ No interview found for token {token}")
        except Exception as e:
            print(f"💥 Error with token {token}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_real_tokens())