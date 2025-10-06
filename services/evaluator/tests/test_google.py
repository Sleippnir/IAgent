#!/usr/bin/env python3

import asyncio
from app.infrastructure.llm_provider import call_google_gemini

async def test_google():
    try:
        result = await call_google_gemini('Say hello briefly', 'No rubric needed', 'Test transcript')
        print('Google API SUCCESS:', result[:100])
        return True
    except Exception as e:
        print('Google API ERROR:', str(e))
        return False

if __name__ == "__main__":
    success = asyncio.run(test_google())
    print(f"Google API working: {success}")