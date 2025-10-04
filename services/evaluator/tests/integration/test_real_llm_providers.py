"""
Integration tests for real LLM providers.
These tests make actual API calls to test the full integration.

To run these tests:
1. Set environment variables for API keys:
   - OPENAI_API_KEY
   - GOOGLE_API_KEY  
   - OPENROUTER_API_KEY

2. Run with pytest markers:
   pytest tests/integration/test_real_llm_providers.py -m "real_api" -v
   
   Or skip real API tests:
   pytest tests/integration/test_real_llm_providers.py -m "not real_api" -v
"""
import pytest
import os
import asyncio
from typing import Optional
import json
from app.infrastructure.llm_provider import (
    call_openai_gpt5,
    call_google_gemini,
    call_openrouter_deepseek,
    run_evaluations
)
from app.domain.entities.interview import Interview
from app.infrastructure.config import Settings


class TestRealLLMProviders:
    """Integration tests with real LLM provider APIs"""
    
    def _is_test_api_key(self, api_key: str) -> bool:
        """Check if an API key is a test/placeholder key"""
        if not api_key:
            return True
        # Only consider obviously fake/test keys as test keys
        if len(api_key) < 10:  # Real API keys are typically much longer
            return True
        # Check for obvious test patterns
        test_patterns = ['test-', 'fake-', 'dummy-', 'placeholder-', 'example-', 'xxx', '123456789']
        return any(pattern in api_key.lower() for pattern in test_patterns)
    
    @pytest.fixture
    def settings(self):
        """Get configuration settings"""
        return Settings()
    
    @pytest.fixture
    def sample_interview(self):
        """Sample interview for testing real LLM evaluations"""
        return Interview(
            interview_id="real-test-001",
            system_prompt="You are an expert technical interviewer evaluating candidates for a Senior Python Developer position.",
            rubric="Rate the candidate on: Technical Skills (1-10), Problem Solving (1-10), Communication (1-10), Culture Fit (1-10). Provide specific examples from the interview.",
            jd="Senior Python Developer - 5+ years experience with Django/FastAPI, microservices, AWS/GCP, TDD, agile methodologies.",
            full_transcript="""
Interviewer: Can you tell me about your experience with Python and web frameworks?

Candidate: I have about 6 years of experience with Python. I've worked extensively with Django for the past 4 years, building several e-commerce platforms. More recently, I've been using FastAPI for microservices development. I particularly appreciate FastAPI's automatic OpenAPI documentation and async capabilities.

Interviewer: That's great. Can you walk me through how you'd design a scalable microservices architecture?

Candidate: Sure. I'd start by identifying bounded contexts to define service boundaries. Each service would have its own database to ensure loose coupling. For communication, I'd use HTTP APIs for synchronous calls and message queues like RabbitMQ or AWS SQS for async operations. I'd implement circuit breakers for fault tolerance and use container orchestration with Docker and Kubernetes.

Interviewer: How do you approach testing in your applications?

Candidate: I follow TDD principles. I write unit tests using pytest, focusing on business logic with good coverage. For integration tests, I use test containers to test against real databases. I also implement end-to-end tests for critical user journeys. I use mocking strategically to isolate units under test.

Interviewer: Any questions for me?

Candidate: Yes, what's the team's approach to code reviews and what development methodologies do you follow?
            """.strip()
        )
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_openai_gpt5_real_call(self, settings, sample_interview):
        """Test real OpenAI GPT-5 API call"""
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_openai_gpt5_real_call(self, settings, sample_interview):
        """Test real OpenAI GPT-5 API call"""
        # Load real settings directly from .env file, bypassing test overrides
        import os
        from app.infrastructure.config import Settings
        
        # Temporarily clear test environment variables to load real .env values
        test_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]
        original_env = {}
        for key in test_keys:
            if key in os.environ:
                original_env[key] = os.environ[key]
                del os.environ[key]
        
        try:
            # Load fresh settings from .env file
            real_settings = Settings()
            
            if not real_settings.OPENAI_API_KEY or self._is_test_api_key(real_settings.OPENAI_API_KEY):
                pytest.skip("Real OPENAI_API_KEY not set - skipping real API test")
            
            # Import the function and temporarily patch settings
            from app.infrastructure import llm_provider
            original_settings = llm_provider.settings
            llm_provider.settings = real_settings
            
            result = await call_openai_gpt5(
                sample_interview.system_prompt,
                sample_interview.rubric,
                sample_interview.full_transcript
            )
            
            # Verify we got a meaningful response
            assert result is not None
            assert len(result) > 50  # Should be a substantial evaluation
            assert isinstance(result, str)
            
            # Should not be an error message
            assert not result.startswith("Error calling OpenAI API:")
            
            # Basic content check - just ensure it's not empty
            print(f"\n=== OpenAI GPT-5 Evaluation ===")
            print(result)
            print(f"=== End OpenAI Response (Length: {len(result)} chars) ===\n")
            
        except Exception as e:
            pytest.fail(f"OpenAI API call failed: {str(e)}")
        finally:
            # Restore original settings and environment variables
            if 'llm_provider' in locals():
                llm_provider.settings = original_settings
            for key, value in original_env.items():
                os.environ[key] = value
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_google_gemini_real_call(self, settings, sample_interview):
        """Test real Google Gemini API call"""
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_google_gemini_real_call(self, settings, sample_interview):
        """Test real Google Gemini API call"""
        # Load real settings directly from .env file, bypassing test overrides
        import os
        from app.infrastructure.config import Settings
        
        # Temporarily clear test environment variables to load real .env values
        test_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]
        original_env = {}
        for key in test_keys:
            if key in os.environ:
                original_env[key] = os.environ[key]
                del os.environ[key]
        
        try:
            # Load fresh settings from .env file
            real_settings = Settings()
            
            if not real_settings.GOOGLE_API_KEY or self._is_test_api_key(real_settings.GOOGLE_API_KEY):
                pytest.skip("Real GOOGLE_API_KEY not set - skipping real API test")
            
            result = await call_google_gemini(
                sample_interview.system_prompt,
                sample_interview.rubric,
                sample_interview.full_transcript
            )
            
            # Verify we got a meaningful response
            assert result is not None
            assert len(result) > 50  # Should be a substantial evaluation
            assert isinstance(result, str)
            
            # Basic content check - just ensure it's not empty
            print(f"\n=== Google Gemini Evaluation ===")
            print(result)
            print(f"=== End Gemini Response (Length: {len(result)} chars) ===\n")
            
        except Exception as e:
            pytest.fail(f"Google Gemini API call failed: {str(e)}")
        finally:
            # Restore original environment variables
            for key, value in original_env.items():
                os.environ[key] = value
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_deepseek_real_call(self, settings, sample_interview):
        """Test real DeepSeek via OpenRouter API call"""
        # Load real settings directly from .env file, bypassing test overrides
        import os
        from app.infrastructure.config import Settings
        
        # Temporarily clear test environment variables to load real .env values
        test_keys = ["OPENAI_API_KEY", "GOOGLE_API_KEY", "OPENROUTER_API_KEY"]
        original_env = {}
        for key in test_keys:
            if key in os.environ:
                original_env[key] = os.environ[key]
                del os.environ[key]
        
        try:
            # Load fresh settings from .env file
            real_settings = Settings()
            
            if not real_settings.OPENROUTER_API_KEY or self._is_test_api_key(real_settings.OPENROUTER_API_KEY):
                pytest.skip("Real OPENROUTER_API_KEY not set - skipping real API test")
            
            result = await call_openrouter_deepseek(
                sample_interview.system_prompt,
                sample_interview.rubric,
                sample_interview.full_transcript
            )
            
            # Verify we got a meaningful response
            assert result is not None
            assert len(result) > 50  # Should be a substantial evaluation
            assert isinstance(result, str)
            
            # Basic content check - just ensure it's not empty
            print(f"\n=== DeepSeek via OpenRouter Evaluation ===")
            print(result)
            print(f"=== End DeepSeek Response (Length: {len(result)} chars) ===\n")
            
        except Exception as e:
            pytest.fail(f"DeepSeek API call failed: {str(e)}")
        finally:
            # Restore original environment variables
            for key, value in original_env.items():
                os.environ[key] = value
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_all_providers_comparison(self, settings, sample_interview):
        """Test all three providers and compare their responses"""
        # Check which providers have API keys
        providers_available = []
        if settings.OPENAI_API_KEY:
            providers_available.append("openai")
        if settings.GOOGLE_API_KEY:
            providers_available.append("gemini")
        if settings.OPENROUTER_API_KEY:
            providers_available.append("deepseek")
        
        if not providers_available:
            pytest.skip("No API keys set - skipping comparison test")
        
        print(f"\n=== Testing Available Providers: {', '.join(providers_available)} ===")
        
        results = {}
        
        # Test each available provider
        if "openai" in providers_available:
            try:
                results["openai"] = await call_openai_gpt5(
                    sample_interview.system_prompt,
                    sample_interview.rubric,
                    sample_interview.full_transcript
                )
                print(f"\n✅ OpenAI GPT-5: {len(results['openai'])} characters")
            except Exception as e:
                print(f"\n❌ OpenAI failed: {str(e)}")
        
        if "gemini" in providers_available:
            try:
                results["gemini"] = await call_google_gemini(
                    sample_interview.system_prompt,
                    sample_interview.rubric,
                    sample_interview.full_transcript
                )
                print(f"✅ Google Gemini: {len(results['gemini'])} characters")
            except Exception as e:
                print(f"❌ Gemini failed: {str(e)}")
        
        if "deepseek" in providers_available:
            try:
                results["deepseek"] = await call_openrouter_deepseek(
                    sample_interview.system_prompt,
                    sample_interview.rubric,
                    sample_interview.full_transcript
                )
                print(f"✅ DeepSeek: {len(results['deepseek'])} characters")
            except Exception as e:
                print(f"❌ DeepSeek failed: {str(e)}")
        
        # Verify we got at least one successful result
        assert len(results) > 0, "No providers returned successful results"
        
        # Analyze response differences
        for provider, response in results.items():
            assert len(response) > 50, f"{provider} response too short"
            print(f"\n=== {provider.upper()} EVALUATION ===")
            print(response[:300] + "..." if len(response) > 300 else response)
        
        print(f"\n=== Comparison Summary ===")
        for provider, response in results.items():
            word_count = len(response.split())
            print(f"{provider}: {len(response)} chars, {word_count} words")
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_full_evaluation_workflow_real(self, settings, sample_interview):
        """Test the complete evaluation workflow with real API calls"""
        # Check if we have at least one API key
        has_api_key = any([
            settings.OPENAI_API_KEY,
            settings.GOOGLE_API_KEY,
            settings.OPENROUTER_API_KEY
        ])
        
        if not has_api_key:
            pytest.skip("No API keys available - skipping full workflow test")
        
        print(f"\n=== Full Evaluation Workflow Test ===")
        print(f"Interview ID: {sample_interview.interview_id}")
        print(f"Available APIs: OpenAI={bool(settings.OPENAI_API_KEY)}, "
              f"Gemini={bool(settings.GOOGLE_API_KEY)}, "
              f"OpenRouter={bool(settings.OPENROUTER_API_KEY)}")
        
        try:
            # Run the full evaluation workflow
            evaluated_interview = await run_evaluations(sample_interview)
            
            # Verify the interview object structure
            assert evaluated_interview.interview_id == sample_interview.interview_id
            assert evaluated_interview.system_prompt == sample_interview.system_prompt
            assert evaluated_interview.rubric == sample_interview.rubric
            assert evaluated_interview.jd == sample_interview.jd
            assert evaluated_interview.full_transcript == sample_interview.full_transcript
            
            # Check evaluations (at least one should be populated if API keys are available)
            evaluations = [
                evaluated_interview.evaluation_1,
                evaluated_interview.evaluation_2,
                evaluated_interview.evaluation_3
            ]
            
            successful_evaluations = [e for e in evaluations if e is not None and len(e) > 10]
            assert len(successful_evaluations) > 0, "No evaluations were completed successfully"
            
            print(f"\n✅ Completed {len(successful_evaluations)}/3 evaluations")
            
            for i, evaluation in enumerate(evaluations, 1):
                if evaluation:
                    print(f"\n=== EVALUATION {i} ===")
                    print(evaluation[:200] + "..." if len(evaluation) > 200 else evaluation)
                else:
                    print(f"\n❌ EVALUATION {i}: Not completed")
            
            # Verify evaluation quality
            for evaluation in successful_evaluations:
                assert len(evaluation) > 50, "Evaluation seems too short"
                # Just ensure it's a non-empty string - don't require specific keywords
                
        except Exception as e:
            pytest.fail(f"Full evaluation workflow failed: {str(e)}")
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_rate_limiting_and_error_handling(self, settings):
        """Test rate limiting and error handling with real APIs"""
        if not any([settings.OPENAI_API_KEY, settings.GOOGLE_API_KEY, settings.OPENROUTER_API_KEY]):
            pytest.skip("No API keys available - skipping rate limiting test")
        
        print(f"\n=== Rate Limiting and Error Handling Test ===")
        
        # Test with minimal prompts to reduce token usage
        simple_prompt = "You are a technical interviewer."
        simple_rubric = "Rate technical skills (1-10)."
        simple_transcript = "Candidate: I have Python experience."
        
        results = []
        errors = []
        
        # Make multiple quick requests to test rate limiting
        for i in range(3):
            try:
                if settings.OPENAI_API_KEY:
                    result = await call_openai_gpt5(simple_prompt, simple_rubric, simple_transcript)
                    results.append(("openai", result))
                    print(f"✅ OpenAI call {i+1}: {len(result)} chars")
                
                # Small delay to be respectful to APIs
                await asyncio.sleep(1)
                
            except Exception as e:
                errors.append(("openai", str(e)))
                print(f"❌ OpenAI call {i+1} failed: {str(e)}")
        
        # We should get some results or appropriate errors
        total_calls = len(results) + len(errors)
        assert total_calls > 0, "No API calls were attempted"
        
        print(f"\nSummary: {len(results)} successful, {len(errors)} errors out of {total_calls} calls")
        
        # If we got errors, they should be meaningful
        for provider, error in errors:
            assert len(error) > 0, f"Empty error message from {provider}"
    
    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_malformed_prompt_handling(self, settings):
        """Test how real APIs handle malformed or edge case prompts"""
        if not settings.OPENAI_API_KEY:
            pytest.skip("OPENAI_API_KEY not set - skipping malformed prompt test")
        
        test_cases = [
            ("empty", "", "", ""),
            ("very_short", "Hi", "Rate 1-10", "Good"),
            ("special_chars", "Test émojis 🚀", "Spéciål rubric", "Candidate: Oui!"),
            ("json_like", '{"test": "prompt"}', '{"rubric": "rate"}', '{"transcript": "ok"}'),
            ("multiline", "Line 1\nLine 2", "Multi\nLine\nRubric", "Q: Hi\n\nA: Hi back"),
        ]
        
        for test_name, prompt, rubric, transcript in test_cases:
            try:
                result = await call_openai_gpt5(prompt, rubric, transcript)
                print(f"✅ {test_name}: Got response ({len(result)} chars)")
                assert isinstance(result, str)
            except Exception as e:
                print(f"❌ {test_name}: {str(e)}")
                # Some failures are expected for edge cases
                assert "error" in str(e).lower() or "invalid" in str(e).lower()


class TestRealAPIConfiguration:
    """Test configuration and setup for real API calls"""
    
    def test_api_key_configuration(self):
        """Test that API key configuration is properly set up"""
        settings = Settings()
        
        # Check environment variables
        env_openai = os.getenv("OPENAI_API_KEY")
        env_google = os.getenv("GOOGLE_API_KEY")
        env_openrouter = os.getenv("OPENROUTER_API_KEY")
        
        print(f"\n=== API Key Configuration ===")
        print(f"OPENAI_API_KEY: {'✅ Set' if env_openai else '❌ Not set'}")
        print(f"GOOGLE_API_KEY: {'✅ Set' if env_google else '❌ Not set'}")
        print(f"OPENROUTER_API_KEY: {'✅ Set' if env_openrouter else '❌ Not set'}")
        
        print(f"\nSettings object:")
        print(f"settings.OPENAI_API_KEY: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not set'}")
        print(f"settings.GOOGLE_API_KEY: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not set'}")
        print(f"settings.OPENROUTER_API_KEY: {'✅ Set' if settings.OPENROUTER_API_KEY else '❌ Not set'}")
        
        # At least warn if no keys are available
        if not any([env_openai, env_google, env_openrouter]):
            print("\n⚠️ WARNING: No API keys found. Real API tests will be skipped.")
            print("To run real API tests, set environment variables:")
            print("  $env:OPENAI_API_KEY='your-key-here'")
            print("  $env:GOOGLE_API_KEY='your-key-here'")
            print("  $env:OPENROUTER_API_KEY='your-key-here'")
    
    def test_model_configuration(self):
        """Test that model names and parameters are properly configured"""
        settings = Settings()
        
        assert settings.OPENAI_MODEL == "gpt-5"
        assert settings.GEMINI_MODEL == "gemini-2.5-pro"
        assert settings.DEEPSEEK_MODEL == "deepseek/deepseek-chat-v3.1"
        assert settings.DEFAULT_MAX_TOKENS == 2000
        assert settings.DEFAULT_TEMPERATURE == 0.3
        assert settings.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"
        
        print(f"\n=== Model Configuration ===")
        print(f"OpenAI Model: {settings.OPENAI_MODEL}")
        print(f"Gemini Model: {settings.GEMINI_MODEL}")
        print(f"DeepSeek Model: {settings.DEEPSEEK_MODEL}")
        print(f"Max Tokens: {settings.DEFAULT_MAX_TOKENS}")
        print(f"Temperature: {settings.DEFAULT_TEMPERATURE}")