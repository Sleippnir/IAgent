#!/usr/bin/env python3
"""
Quick test to see what tables exist in Supabase
"""
import asyncio
import httpx
from app.infrastructure.config import Settings

async def list_tables():
    """List available tables in Supabase"""
    settings = Settings()
    
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    # Common table names to test
    table_candidates = [
        "interview_queue", "interviews_queue", "interviews", 
        "evaluator_queue", "evaluators_queue", "evaluations",
        "transcripts", "transcript"
    ]
    
    async with httpx.AsyncClient() as client:
        print("🔍 Testing table accessibility...")
        
        for table in table_candidates:
            try:
                url = f"{settings.SUPABASE_URL}/rest/v1/{table}?limit=1"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Table '{table}' exists and accessible - {len(data)} record(s) found")
                    if data:
                        print(f"   📋 Sample fields: {list(data[0].keys())}")
                elif response.status_code == 404:
                    print(f"❌ Table '{table}' not found (404)")
                elif response.status_code == 401:
                    print(f"🔐 Table '{table}' exists but unauthorized (401)")
                else:
                    print(f"⚠️  Table '{table}' - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"💥 Error testing table '{table}': {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_tables())