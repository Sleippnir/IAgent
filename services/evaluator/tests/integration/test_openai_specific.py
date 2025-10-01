#!/usr/bin/env python3
"""
Test OpenAI API specifically after restriction updates
"""
import sys
import asyncio

sys.path.insert(0, '.')

async def test_openai_only():
    from app.infrastructure.config import Settings
    from app.infrastructure.llm_provider import call_openai_gpt5
    from app.domain.entities.interview import Interview
    import app.infrastructure.llm_provider as llm_provider
    
    settings = Settings()
    llm_provider.settings = settings
    
    print("=== OpenAI API Test (After Restriction Update) ===")
    print(f"OpenAI API Key: {settings.OPENAI_API_KEY[:15]}...{settings.OPENAI_API_KEY[-8:]}")
    print(f"Model: {settings.OPENAI_MODEL}")
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('test-'):
        print("❌ No real OpenAI API key found")
        return False
    
    # Simple test case first
    print("\n=== Test 1: Simple Evaluation ===")
    simple_prompt = "You are a technical interviewer evaluating a Python developer."
    simple_rubric = "Rate technical skills (1-10) and communication (1-10)."
    simple_transcript = """
Interviewer: Tell me about your Python experience.
Candidate: I have 3 years of Python experience with Django and Flask.
Interviewer: How do you handle database queries?
Candidate: I use Django ORM mostly, and sometimes raw SQL for complex queries.
    """.strip()
    
    print(f"Prompt: {simple_prompt}")
    print(f"Transcript length: {len(simple_transcript)} chars")
    
    try:
        result = await call_openai_gpt5(simple_prompt, simple_rubric, simple_transcript)
        
        print(f"\n=== OpenAI Response ===")
        print(f"Response length: {len(result)} characters")
        print(f"Response type: {type(result)}")
        
        if result.startswith("Error calling"):
            print(f"❌ API call failed: {result}")
            # Extract error details
            if "Error code:" in result:
                error_parts = result.split("Error code:")
                if len(error_parts) > 1:
                    error_code = error_parts[1].split("-")[0].strip()
                    print(f"Error Code: {error_code}")
                    
                    if error_code == "429":
                        print("This is a rate limiting or quota issue")
                    elif error_code == "401":
                        print("This is an authentication issue")
                    elif error_code == "403":
                        print("This is a permissions/restriction issue")
            return False
        
        print("\n=== Full Response ===")
        print(result)
        
        # Validate response quality
        result_lower = result.lower()
        has_relevant_content = any(word in result_lower for word in [
            'technical', 'python', 'experience', 'skills', 
            'candidate', 'evaluation', 'rating', 'score', 'django'
        ])
        
        has_scores = any(num in result for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        
        print(f"\n=== Quality Analysis ===")
        print(f"✅ Length check: {len(result)} chars {'PASS' if len(result) > 50 else 'FAIL'}")
        print(f"✅ Relevant content: {'PASS' if has_relevant_content else 'FAIL'}")
        print(f"✅ Contains scores: {'PASS' if has_scores else 'FAIL'}")
        
        if len(result) > 50 and has_relevant_content:
            print("\n🎉 OpenAI API test PASSED!")
            return True
        else:
            print("\n⚠️ Response quality needs improvement")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_openai_detailed():
    """Test with more detailed interview"""
    from app.infrastructure.config import Settings
    from app.infrastructure.llm_provider import call_openai_gpt5
    import app.infrastructure.llm_provider as llm_provider
    
    settings = Settings()
    llm_provider.settings = settings
    
    print("\n=== Test 2: Detailed Interview Evaluation ===")
    
    detailed_prompt = "You are an expert technical interviewer evaluating candidates for a Senior Python Developer position."
    detailed_rubric = "Evaluate on: Technical Skills (1-10), Problem Solving (1-10), Communication (1-10). Provide specific scores and detailed feedback."
    detailed_transcript = """
Interviewer: Can you walk me through your experience with Python web frameworks?

Candidate: I have 5 years of experience with Python. I started with Flask for small APIs, then moved to Django for larger applications. Recently, I've been working with FastAPI for microservices because of its async capabilities and automatic OpenAPI documentation.

Interviewer: How do you approach testing in your Python applications?

Candidate: I follow TDD principles. I write unit tests using pytest, and I use fixtures for test data. For integration tests, I use TestClient for FastAPI or Django's test client. I also implement mocking for external dependencies.

Interviewer: Tell me about a performance optimization you've implemented.

Candidate: We had a Django view that was making N+1 database queries. I optimized it using select_related and prefetch_related to reduce the queries from hundreds to just 3. This improved the response time from 2 seconds to under 200ms.
    """.strip()
    
    print(f"Transcript length: {len(detailed_transcript)} chars")
    
    try:
        result = await call_openai_gpt5(detailed_prompt, detailed_rubric, detailed_transcript)
        
        if result.startswith("Error calling"):
            print(f"❌ Detailed test failed: {result[:200]}...")
            return False
        
        print(f"\n=== Detailed Response ===")
        print(f"Response length: {len(result)} characters")
        print(f"Word count: {len(result.split())} words")
        print("\n--- FULL EVALUATION ---")
        print(result)
        print("--- END EVALUATION ---")
        
        # Advanced analysis
        result_lower = result.lower()
        has_frameworks = any(fw in result_lower for fw in ['django', 'fastapi', 'flask'])
        has_testing = any(test_term in result_lower for test_term in ['test', 'pytest', 'tdd'])
        has_performance = any(perf in result_lower for perf in ['performance', 'optimization', 'query'])
        has_scores = any(f"{i}/10" in result for i in range(1, 11))
        
        print(f"\n=== Advanced Analysis ===")
        print(f"✅ Mentions frameworks: {'PASS' if has_frameworks else 'FAIL'}")
        print(f"✅ Discusses testing: {'PASS' if has_testing else 'FAIL'}")
        print(f"✅ Performance awareness: {'PASS' if has_performance else 'FAIL'}")
        print(f"✅ Proper scoring format: {'PASS' if has_scores else 'FAIL'}")
        
        quality_score = sum([has_frameworks, has_testing, has_performance, has_scores])
        print(f"Overall Quality Score: {quality_score}/4")
        
        if quality_score >= 3:
            print("\n🎉 Detailed OpenAI test PASSED with high quality!")
            return True
        else:
            print("\n⚠️ Response needs improvement")
            return False
            
    except Exception as e:
        print(f"\n❌ Detailed test exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenAI API Specifically")
    
    # Test simple case first
    success1 = asyncio.run(test_openai_only())
    
    if success1:
        # If simple test passes, try detailed test
        success2 = asyncio.run(test_openai_detailed())
    else:
        print("\nSkipping detailed test due to simple test failure")
        success2 = False
    
    print(f"\n=== Final OpenAI Test Results ===")
    print(f"Simple test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Detailed test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 OpenAI API is working perfectly!")
        sys.exit(0)
    elif success1:
        print("\n✅ OpenAI API basic functionality works")
        sys.exit(0)
    else:
        print("\n❌ OpenAI API needs attention")
        sys.exit(1)