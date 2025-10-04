"""Final comprehensive test of all LLM providers - using latest GPT-5 configuration."""

import asyncio
import sys

sys.path.insert(0, '.')

async def test_all_providers():
    """Test all LLM providers to ensure they're working correctly."""
    from app.infrastructure.config import Settings
    from app.infrastructure.llm_provider import call_openai_gpt5, call_google_gemini, call_openrouter_deepseek
    import app.infrastructure.llm_provider as llm_provider
    
    settings = Settings()
    llm_provider.settings = settings
    
    # Test data
    PROMPT = "You are a technical interviewer evaluating a Python developer."
    RUBRIC = """Technical Skills (1-10): Knowledge of Python, frameworks, and best practices
Communication (1-10): Clarity and explanation of concepts"""
    
    TRANSCRIPT = """Interviewer: What Python frameworks have you worked with?
Candidate: I've used Django and Flask extensively. Also worked with FastAPI recently.
Interviewer: Can you describe a challenging technical problem you solved?
Candidate: I optimized a Django application that had N+1 query issues. Used select_related to reduce queries from 200+ to 3."""
    """Test all LLM providers to ensure they're working correctly."""
    print("🚀 FINAL COMPREHENSIVE LLM PROVIDER TEST")
    print("=" * 60)
    
    # Test results
    results = {
        "OpenAI GPT-5": "❌ FAILED",
        "Google Gemini": "❌ FAILED", 
        "DeepSeek v3.1": "❌ FAILED"
    }
    
    # Test 1: OpenAI GPT-5
    print("\n=== TEST 1: OpenAI GPT-5 ===")
    print(f"Model: {settings.OPENAI_MODEL}")
    try:
        response = await call_openai_gpt5(PROMPT, RUBRIC, TRANSCRIPT)
        if response and not response.startswith("Error"):
            print(f"✅ SUCCESS - Response length: {len(response)} chars")
            results["OpenAI GPT-5"] = "✅ PASSED"
            print(f"Preview: {response[:150]}...")
        else:
            print(f"❌ FAILED: {response}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 2: Google Gemini
    print("\n=== TEST 2: Google Gemini ===")
    print(f"Model: {settings.GEMINI_MODEL}")
    try:
        response = await call_google_gemini(PROMPT, RUBRIC, TRANSCRIPT)
        if response and not response.startswith("Error"):
            print(f"✅ SUCCESS - Response length: {len(response)} chars")
            results["Google Gemini"] = "✅ PASSED"
            print(f"Preview: {response[:150]}...")
        else:
            print(f"❌ FAILED: {response}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Test 3: DeepSeek
    print("\n=== TEST 3: DeepSeek v3.1 ===")
    print(f"Model: {settings.DEEPSEEK_MODEL}")
    try:
        response = await call_openrouter_deepseek(PROMPT, RUBRIC, TRANSCRIPT)
        if response and not response.startswith("Error"):
            print(f"✅ SUCCESS - Response length: {len(response)} chars")
            results["DeepSeek v3.1"] = "✅ PASSED"
            print(f"Preview: {response[:150]}...")
        else:
            print(f"❌ FAILED: {response}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
    
    # Final Results
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    for provider, status in results.items():
        print(f"{status} {provider}")
    
    # Summary
    passed_count = sum(1 for status in results.values() if "PASSED" in status)
    total_count = len(results)
    
    print(f"\n📊 SUMMARY: {passed_count}/{total_count} providers working")
    
    if passed_count == total_count:
        print("🎉 ALL LLM PROVIDERS ARE WORKING PERFECTLY!")
    elif passed_count > 0:
        print("⚠️  Some providers working - check failed ones")
    else:
        print("🚨 NO PROVIDERS WORKING - NEEDS ATTENTION")

if __name__ == "__main__":
    asyncio.run(test_all_providers())