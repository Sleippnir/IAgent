#!/usr/bin/env pwsh
# PowerShell script to run LLM integration tests with real API calls
# Usage: .\run_real_api_tests.ps1

Write-Host "=== LLM Real API Integration Tests ===" -ForegroundColor Green

# Check if API keys are set
$hasOpenAI = [bool]$env:OPENAI_API_KEY
$hasGoogle = [bool]$env:GOOGLE_API_KEY
$hasOpenRouter = [bool]$env:OPENROUTER_API_KEY

Write-Host "`nAPI Key Status:" -ForegroundColor Yellow
Write-Host "OPENAI_API_KEY: $(if($hasOpenAI){'✅ Set'}else{'❌ Not set'})"
Write-Host "GOOGLE_API_KEY: $(if($hasGoogle){'✅ Set'}else{'❌ Not set'})"
Write-Host "OPENROUTER_API_KEY: $(if($hasOpenRouter){'✅ Set'}else{'❌ Not set'})"

if (-not ($hasOpenAI -or $hasGoogle -or $hasOpenRouter)) {
    Write-Host "`n⚠️ WARNING: No API keys found!" -ForegroundColor Red
    Write-Host "To run real API tests, set your API keys:" -ForegroundColor Yellow
    Write-Host '$env:OPENAI_API_KEY = "your-openai-key-here"'
    Write-Host '$env:GOOGLE_API_KEY = "your-google-key-here"'  
    Write-Host '$env:OPENROUTER_API_KEY = "your-openrouter-key-here"'
    Write-Host "`nExample for this session:"
    Write-Host '$env:OPENAI_API_KEY = "sk-..."' -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue with configuration test only, or Ctrl+C to exit"
}

Write-Host "`n=== Test Options ===" -ForegroundColor Green
Write-Host "1. Run configuration tests only (no API calls)"
Write-Host "2. Run real API tests (makes actual API calls)"  
Write-Host "3. Run specific provider test"
Write-Host "4. Run comparison test (all available providers)"
Write-Host "5. Run full workflow test"

$choice = Read-Host "`nEnter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`nRunning configuration tests..." -ForegroundColor Cyan
        python -m pytest tests/integration/test_real_llm_providers.py::TestRealAPIConfiguration -v
    }
    "2" {
        Write-Host "`nRunning all real API tests..." -ForegroundColor Cyan
        python -m pytest tests/integration/test_real_llm_providers.py -m "real_api" -v -s
    }
    "3" {
        Write-Host "`nAvailable provider tests:"
        Write-Host "  - test_openai_gpt5_real_call"
        Write-Host "  - test_google_gemini_real_call"
        Write-Host "  - test_deepseek_real_call"
        $provider = Read-Host "Enter test name"
        python -m pytest "tests/integration/test_real_llm_providers.py::TestRealLLMProviders::$provider" -v -s
    }
    "4" {
        Write-Host "`nRunning provider comparison test..." -ForegroundColor Cyan
        python -m pytest tests/integration/test_real_llm_providers.py::TestRealLLMProviders::test_all_providers_comparison -v -s
    }
    "5" {
        Write-Host "`nRunning full workflow test..." -ForegroundColor Cyan
        python -m pytest tests/integration/test_real_llm_providers.py::TestRealLLMProviders::test_full_evaluation_workflow_real -v -s
    }
    default {
        Write-Host "Invalid choice. Running configuration test." -ForegroundColor Yellow
        python -m pytest tests/integration/test_real_llm_providers.py::TestRealAPIConfiguration -v
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green