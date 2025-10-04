# Real API Testing Guide

This guide shows you how to test the LLM service with actual API calls to OpenAI, Google, and DeepSeek.

## Quick Start

### 1. Set API Keys (PowerShell)
```powershell
# Set for current session
$env:OPENAI_API_KEY = "sk-your-openai-key-here"
$env:GOOGLE_API_KEY = "your-google-api-key-here"  
$env:OPENROUTER_API_KEY = "sk-your-openrouter-key-here"

# Or set permanently (optional)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-key", "User")
```

### 2. Run Tests

**Option A: Use the PowerShell script (Recommended)**
```powershell
.\run_real_api_tests.ps1
```

**Option B: Run directly with pytest**
```powershell
# Configuration check (no API calls)
python -m pytest tests/integration/test_real_llm_providers.py::TestRealAPIConfiguration -v

# All real API tests
python -m pytest tests/integration/test_real_llm_providers.py -m "real_api" -v -s

# Specific provider test
python -m pytest tests/integration/test_real_llm_providers.py::TestRealLLMProviders::test_openai_gpt5_real_call -v -s

# Provider comparison
python -m pytest tests/integration/test_real_llm_providers.py::TestRealLLMProviders::test_all_providers_comparison -v -s

# Full workflow
python -m pytest tests/integration/test_real_llm_providers.py::TestRealLLMProviders::test_full_evaluation_workflow_real -v -s
```

## API Key Setup

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Set: `$env:OPENAI_API_KEY = "sk-..."`

### Google (Gemini)
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Set: `$env:GOOGLE_API_KEY = "AI..."`

### OpenRouter (for DeepSeek)
1. Go to https://openrouter.ai/keys
2. Create API key  
3. Set: `$env:OPENROUTER_API_KEY = "sk-..."`

## Test Categories

### 1. Configuration Tests
- ✅ No API calls
- Checks environment setup
- Validates model configuration

### 2. Individual Provider Tests
- ⚠️ Makes real API calls
- Tests each LLM provider separately
- Validates response quality

### 3. Comparison Tests
- ⚠️ Makes multiple API calls
- Compares responses from different providers
- Shows response differences

### 4. Workflow Tests
- ⚠️ Makes real API calls
- Tests full evaluation pipeline
- End-to-end integration

### 5. Error Handling Tests
- ⚠️ Makes real API calls
- Tests rate limiting
- Tests malformed inputs

## Cost Considerations

- **OpenAI GPT-5**: ~$0.01-0.05 per test
- **Google Gemini**: Usually free tier available
- **OpenRouter DeepSeek**: ~$0.001-0.01 per test

Total cost for full test suite: Usually under $0.50

## Expected Test Output

### Successful API Call
```
=== OpenAI GPT-5 Evaluation ===
Based on the interview transcript, I'll evaluate this candidate:

Technical Skills (9/10): Demonstrates strong Python experience with 6 years...
[detailed evaluation continues]
=== End OpenAI Response (Length: 1247 chars) ===
```

### Provider Comparison
```
=== Testing Available Providers: openai, gemini, deepseek ===
✅ OpenAI GPT-5: 1247 characters
✅ Google Gemini: 892 characters  
✅ DeepSeek: 1056 characters

=== Comparison Summary ===
openai: 1247 chars, 198 words
gemini: 892 chars, 142 words
deepseek: 1056 chars, 167 words
```

## Troubleshooting

### Common Issues

**❌ "API key not set" errors**
- Solution: Set environment variables properly
- Check: `echo $env:OPENAI_API_KEY`

**❌ "401 Unauthorized" errors**  
- Check API key is valid and active
- Verify billing/usage limits

**❌ "429 Rate limit" errors**
- Normal for rapid testing
- Tests include delays between calls

**❌ Import errors**
- Run: `uv pip install -r requirements.txt`
- Ensure all dependencies installed

### Debug Mode
Add `-s` flag to see full output:
```powershell
python -m pytest tests/integration/test_real_llm_providers.py -m "real_api" -v -s
```

## Test Structure

```
tests/integration/test_real_llm_providers.py
├── TestRealLLMProviders          # Real API call tests
│   ├── test_openai_gpt5_real_call
│   ├── test_google_gemini_real_call  
│   ├── test_deepseek_real_call
│   ├── test_all_providers_comparison
│   ├── test_full_evaluation_workflow_real
│   ├── test_rate_limiting_and_error_handling
│   └── test_malformed_prompt_handling
└── TestRealAPIConfiguration      # Configuration tests
    ├── test_api_key_configuration
    └── test_model_configuration
```

## Sample Interview Data

The tests use a realistic interview scenario:
- **Role**: Senior Python Developer
- **Candidate**: 6 years Python experience
- **Topics**: Django, FastAPI, microservices, testing
- **Transcript**: ~500 words of realistic Q&A

This provides a good test case for evaluation quality.