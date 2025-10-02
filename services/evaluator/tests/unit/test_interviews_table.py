#!/usr/bin/env python3
"""
Check the structure of the interviews table
"""
import asyncio
import httpx
from app.infrastructure.config import Settings

async def explore_interviews_table():
    """Explore the interviews table structure"""
    settings = Settings()
    
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        print("🔍 Exploring interviews table...")
        
        try:
            # Get a few records to see structure
            url = f"{settings.SUPABASE_URL}/rest/v1/interviews?limit=3"
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data)} record(s) in interviews table")
                
                if data:
                    print(f"\n📋 Sample record fields: {list(data[0].keys())}")
                    
                    for i, record in enumerate(data):
                        print(f"\n🔍 Record {i+1}:")
                        for key, value in record.items():
                            if isinstance(value, str) and len(value) < 100:
                                print(f"  {key}: {value}")
                            elif isinstance(value, (int, float, bool, type(None))):
                                print(f"  {key}: {value}")
                            else:
                                print(f"  {key}: <{type(value).__name__}> (length: {len(str(value))})")
                                
                    # Check if there's a specific interview_id we're looking for
                    target_id = "66b750ad-1196-471f-bedb-99b0328d7e30"
                    print(f"\n🎯 Looking for specific interview: {target_id}")
                    
                    url_specific = f"{settings.SUPABASE_URL}/rest/v1/interviews?interview_id=eq.{target_id}"
                    response_specific = await client.get(url_specific, headers=headers)
                    
                    if response_specific.status_code == 200:
                        specific_data = response_specific.json()
                        if specific_data:
                            print(f"✅ Found target interview")
                            print(f"📋 Fields: {list(specific_data[0].keys())}")
                            for key, value in specific_data[0].items():
                                print(f"  {key}: {value}")
                        else:
                            print(f"❌ Target interview not found in interviews table")
                    else:
                        print(f"❌ Error querying specific interview: {response_specific.status_code}")
                        
                else:
                    print("❌ No records found in interviews table")
                    
            else:
                print(f"❌ Error accessing interviews table: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"💥 Error exploring interviews table: {str(e)}")

if __name__ == "__main__":
    asyncio.run(explore_interviews_table())