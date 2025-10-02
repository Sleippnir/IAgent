#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.helpers import call_openai_gpt5

async def test_api():
    try:
        result = await call_openai_gpt5('Say hello briefly', 'No rubric needed', 'Test transcript')
        print('OpenAI API SUCCESS:', result[:100])
        return True
    except Exception as e:
        print('OpenAI API ERROR:', str(e))
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    print(f"API working: {success}")