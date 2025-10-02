#!/usr/bin/env python3
"""
Test to see what's actually in the interviewer_queue table
"""
import asyncio
import httpx
from app.infrastructure.config import Settings

async def explore_interviewer_queue():
    """Explore the interviewer_queue table structure and data"""
    settings = Settings()
    
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print("🔍 Exploring interviewer_queue table...")
        
        try:
            # Get all records to see structure
            url = f"{settings.SUPABASE_URL}/rest/v1/interviewer_queue?limit=5"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} record(s) in interviewer_queue")
                
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
                    print("❌ No records found in interviewer_queue")
                    
            else:
                print(f"❌ Error accessing interviewer_queue: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"💥 Error exploring interviewer_queue: {str(e)}")

if __name__ == "__main__":
    asyncio.run(explore_interviewer_queue())