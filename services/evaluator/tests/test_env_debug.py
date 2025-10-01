#!/usr/bin/env python3

import pytest
import os
from app.infrastructure.config import Settings

@pytest.mark.asyncio 
async def test_debug_environment():
    """Debug what environment variables are actually set"""
    print("\n=== Environment Variables ===")
    print(f"os.environ GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY', 'NOT SET')[:15]}...")
    print(f"os.environ OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')[:15]}...")
    
    print("\n=== Settings Instance ===")
    settings = Settings()
    print(f"Settings GOOGLE_API_KEY: {settings.GOOGLE_API_KEY[:15] if settings.GOOGLE_API_KEY else 'None'}...")
    print(f"Settings OPENAI_API_KEY: {settings.OPENAI_API_KEY[:15] if settings.OPENAI_API_KEY else 'None'}...")

if __name__ == "__main__":
    import subprocess
    result = subprocess.run(['pytest', __file__ + '::test_debug_environment', '-v', '-s'], capture_output=False)