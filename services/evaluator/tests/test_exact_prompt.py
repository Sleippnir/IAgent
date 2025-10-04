#!/usr/bin/env python3

import asyncio
from app.infrastructure.llm_provider import call_google_gemini

async def test_exact_sample():
    system_prompt = "You are an expert technical interviewer evaluating candidates for a Senior Python Developer position."
    rubric = "Rate the candidate on: Technical Skills (1-10), Problem Solving (1-10), Communication (1-10), Culture Fit (1-10). Provide specific examples from the interview."
    transcript = """
Interviewer: Can you tell me about your experience with Python and web frameworks?

Candidate: I have about 6 years of experience with Python. I've worked extensively with Django for the past 4 years, building several e-commerce platforms. More recently, I've been using FastAPI for microservices development. I particularly appreciate FastAPI's automatic OpenAPI documentation and async capabilities.

Interviewer: That's great. Can you walk me through how you'd design a scalable microservices architecture?

Candidate: Sure. I'd start by identifying bounded contexts to define service boundaries. Each service would have its own database to ensure loose coupling. For communication, I'd use HTTP APIs for synchronous calls and message queues like RabbitMQ or AWS SQS for async operations. I'd implement circuit breakers for fault tolerance and use container orchestration with Docker and Kubernetes.

Interviewer: How do you approach testing in your applications?

Candidate: I follow TDD principles. I write unit tests using pytest, focusing on business logic with good coverage. For integration tests, I use test containers to test against real databases. I also implement end-to-end tests for critical user journeys. I use mocking strategically to isolate units under test.

Interviewer: Any questions for me?

Candidate: Yes, what's the team's approach to code reviews and what development methodologies do you follow?
    """.strip()
    
    try:
        result = await call_google_gemini(system_prompt, rubric, transcript)
        print(f"=== Google Response (Length: {len(result)}) ===")
        print(result)
        print("=== End Response ===\n")
        
        # Check for the specific words the test is looking for
        result_lower = result.lower()
        expected_words = ['technical', 'python', 'experience', 'skills']
        found_words = [word for word in expected_words if word in result_lower]
        
        print(f"Expected words: {expected_words}")
        print(f"Found words: {found_words}")
        print(f"Test would pass: {len(found_words) > 0}")
        
        return len(found_words) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_exact_sample())
    print(f"Test passes: {success}")