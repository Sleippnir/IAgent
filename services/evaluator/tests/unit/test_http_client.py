#!/usr/bin/env python3
"""
Test the HTTP client directly
"""
import asyncio
from app.infrastructure.persistence.supabase.client import get_supabase_client

async def test_http_client():
    """Test the HTTP client directly"""
    client = get_supabase_client()
    
    # Test with a known auth token
    token = "5485f72a-bb59-4a72-8bec-bd1ed08d1c75"
    
    print(f"🔍 Testing HTTP client with token: {token}")
    
    try:
        # Test direct HTTP client call
        results = await client.get("interviewer_queue", {"auth_token": token})
        
        if results:
            print(f"✅ HTTP client returned {len(results)} result(s)")
            for i, result in enumerate(results):
                print(f"📋 Result {i+1} keys: {list(result.keys())}")
        else:
            print("❌ HTTP client returned no results")
            
    except Exception as e:
        print(f"💥 HTTP client error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_http_client())