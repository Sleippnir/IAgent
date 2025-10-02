#!/usr/bin/env python3
"""
Final verification - check if the completed interview triggers evaluator_queue population
"""
import asyncio
from app.infrastructure.persistence.supabase.services import QueueService

async def check_evaluator_queue():
    """Check if completed interviews appear in evaluator_queue"""
    
    print("🔍 Checking if completed interviews triggered evaluator_queue population...")
    
    queue_service = QueueService()
    
    try:
        # Check evaluator_queue for any records
        evaluator_tasks = await queue_service.client.get("evaluator_queue", {"limit": 5})
        
        if evaluator_tasks:
            print(f"✅ Found {len(evaluator_tasks)} evaluation task(s) in evaluator_queue!")
            
            for i, task in enumerate(evaluator_tasks, 1):
                print(f"\n📋 Evaluation Task {i}:")
                print(f"   🆔 Interview ID: {task.get('interview_id', 'N/A')}")
                print(f"   🔗 Auth Token: {task.get('auth_token', 'N/A')}")
                print(f"   📅 Created: {task.get('created_at', 'N/A')}")
                
                # Check if this has a payload ready for evaluation
                payload = task.get('payload', {})
                if payload:
                    print(f"   📦 Payload ready: ✅")
                    print(f"   👤 Candidate: {payload.get('candidate_name', 'N/A')}")
                    print(f"   💼 Job: {payload.get('job_title', 'N/A')}")
                    
                    # Test if we can create an Interview for evaluation
                    try:
                        from app.domain.entities.interview import Interview
                        interview = Interview.from_json(payload)
                        print(f"   🧪 Interview instance: ✅ {interview}")
                        print(f"   🤖 Ready for LLM evaluation: ✅")
                    except Exception as e:
                        print(f"   💥 Interview creation error: {str(e)}")
                else:
                    print(f"   📦 Payload: ❌ Missing")
                    
            print(f"\n🎯 Evaluator service can now process these completed interviews!")
                    
        else:
            print("❌ No evaluation tasks found in evaluator_queue")
            print("💡 This means:")
            print("   - No interviews have been completed and moved to evaluator_queue yet")
            print("   - Or the automatic trigger hasn't run yet")
            print("   - The transcript writing worked, but evaluator_queue population is pending")
            
    except Exception as e:
        print(f"💥 Error checking evaluator_queue: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_evaluator_queue())