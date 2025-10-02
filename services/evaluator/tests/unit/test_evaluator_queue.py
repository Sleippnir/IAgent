#!/usr/bin/env python3
"""
Check what's in the evaluator_queue table
"""
import asyncio
import httpx
from app.infrastructure.config import Settings

async def explore_evaluator_queue():
    """Explore the evaluator_queue table structure and data"""
    settings = Settings()
    
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print("🔍 Exploring evaluator_queue table...")
        
        try:
            # Get all records to see structure
            url = f"{settings.SUPABASE_URL}/rest/v1/evaluator_queue?limit=5"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} record(s) in evaluator_queue")
                
                if data:
                    print(f"\n📋 Sample record fields: {list(data[0].keys())}")
                    
                    for i, record in enumerate(data[:3]):  # Show first 3 records
                        print(f"\n🔍 Record {i+1}:")
                        for key, value in record.items():
                            if isinstance(value, str) and len(value) < 200:
                                print(f"  {key}: {value}")
                            elif isinstance(value, (int, float, bool, type(None))):
                                print(f"  {key}: {value}")
                            else:
                                print(f"  {key}: <{type(value).__name__}> (length: {len(str(value))})")
                else:
                    print("❌ No records found in evaluator_queue")
                    
            else:
                print(f"❌ Error accessing evaluator_queue: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"💥 Error exploring evaluator_queue: {str(e)}")

if __name__ == "__main__":
    asyncio.run(explore_evaluator_queue())