#!/usr/bin/env python3

import pytest
from app.infrastructure.llm_provider import settings as llm_settings
from app.infrastructure.config import Settings

@pytest.mark.asyncio 
async def test_settings_comparison():
    """Compare the global llm_provider settings vs new Settings instance"""
    print("\n=== Settings Comparison ===")
    
    print(f"llm_provider.settings.GOOGLE_API_KEY: {llm_settings.GOOGLE_API_KEY[:15] if llm_settings.GOOGLE_API_KEY else 'None'}...")
    print(f"llm_provider.settings.OPENAI_API_KEY: {llm_settings.OPENAI_API_KEY[:15] if llm_settings.OPENAI_API_KEY else 'None'}...")
    
    new_settings = Settings()
    print(f"new Settings().GOOGLE_API_KEY: {new_settings.GOOGLE_API_KEY[:15] if new_settings.GOOGLE_API_KEY else 'None'}...")
    print(f"new Settings().OPENAI_API_KEY: {new_settings.OPENAI_API_KEY[:15] if new_settings.OPENAI_API_KEY else 'None'}...")
    
    print(f"Same instance? {llm_settings is new_settings}")
    print(f"Google keys equal? {llm_settings.GOOGLE_API_KEY == new_settings.GOOGLE_API_KEY}")

if __name__ == "__main__":
    import subprocess
    result = subprocess.run(['pytest', __file__ + '::test_settings_comparison', '-v', '-s'], capture_output=False)