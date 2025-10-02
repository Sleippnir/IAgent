# IAgent Development Guidelines

## 🎯 Purpose
This document provides specific development guidelines for the IAgent AI interview platform. These guidelines ensure consistent, maintainable, and scalable code across all microservices in this project.

## 📋 Core Principles

### 1. Separation of Concerns
- **Each file should have a single, well-defined responsibility**
- **No file should exceed 500 lines of code** (aim for 200-300 lines)
- **Split functionality when files become too large or handle multiple concerns**
- **Each project/service within a monorepo should follow its own modular structure**

## 🏗️ IAgent Architecture Structure

### **Current Microservices**
```
IAgent/
├── api-gateway/              # FastAPI gateway (Port 8000)
│   ├── main.py              # Gateway entry point
│   ├── app/
│   │   ├── middleware/      # Auth, CORS, rate limiting
│   │   ├── routes/          # Route definitions
│   │   └── utils/           # Gateway utilities
│   └── requirements.txt
├── services/
│   ├── core/                # User management & business logic (Port 8001)
│   │   ├── main.py
│   │   └── app/
│   │       ├── application/ # Use cases
│   │       ├── domain/      # Business entities
│   │       └── infrastructure/ # Config, DB access
│   ├── evaluator/           # LLM-based evaluation (Port 8005)
│   │   ├── main.py
│   │   └── app/
│   │       ├── application/ # Evaluation workflows
│   │       ├── domain/      # Evaluation logic
│   │       └── infrastructure/ # LLM integrations
│   └── speech/              # STT/TTS with Pipecat (Port 8002)
│       ├── main.py
│       └── app/
│           ├── routes/      # Speech endpoints
│           └── services/    # Pipecat integration
├── shared/                  # Common utilities
│   └── pyproject.toml       # org_shared package
├── frontend/                # Web interface
├── docs/                    # Project documentation
├── supabase/               # Database backend
└── test_data/              # Sample data & examples
```

### **Technology Stack**
- **Backend**: FastAPI (Python 3.12)
- **Database**: Supabase (PostgreSQL + Auth)
- **AI Services**: OpenAI, Google Gemini, ElevenLabs, Deepgram, DeepSeek
- **Speech/Video**: Pipecat framework with Simli integration
- **Containerization**: Docker (individual Dockerfiles per service)
- **Package Management**: Virtual environments + requirements.txt

### **Service-Specific Patterns**

#### API Gateway Structure
```
api-gateway/
├── main.py                   # FastAPI app with CORS & routing
├── app/
│   ├── middleware/
│   │   └── auth.py          # JWT authentication
│   ├── routes/
│   │   ├── gateway_routes.py # Service routing logic
│   │   └── example.py       # Health checks & examples
│   └── utils/
│       └── helpers.py       # Gateway utilities
├── requirements.txt
└── Dockerfile
```

#### Core Service Structure (Clean Architecture)
```
services/core/
├── main.py                   # FastAPI entry point
├── app/
│   ├── application/          # Use cases (interview workflows)
│   ├── domain/              # Business entities (Interview, Candidate)
│   └── infrastructure/      # External concerns (DB, APIs)
│       └── config.py        # Environment configuration
├── requirements.txt
└── Dockerfile
```

#### Evaluator Service Structure
```
services/evaluator/
├── main.py                   # Evaluation orchestrator
├── app/
│   ├── application/          # Evaluation workflows
│   ├── domain/              # Evaluation models & logic
│   └── infrastructure/      # LLM provider integrations
│       └── config.py        # Provider configurations
├── tests/                   # Comprehensive test suite
├── requirements.txt
└── pyproject.toml
```

#### Speech Service Structure
```
services/speech/
├── main.py                   # FastAPI with Pipecat integration
├── app/
│   ├── routes/              # REST endpoints
│   │   └── speech_routes.py
│   └── services/            # Pipecat orchestration
│       ├── pipecat_simli_test.py # Real-time speech processing
│       └── speech_service.py     # Business logic
├── storage/                 # Transcript storage
├── requirements.txt
└── Dockerfile
```

## 📝 IAgent Development Standards

### **File Size Limits**
- **Python files: 300-500 lines maximum**
- **FastAPI route files: 200-300 lines maximum**  
- **Configuration files: 100-200 lines maximum**
- **Pipecat service files: 400-600 lines** (due to complex orchestration)

### **Naming Conventions**
- **Services**: `[feature]_service.py` (e.g., `evaluation_service.py`)
- **Routes**: `[feature]_routes.py` (e.g., `interview_routes.py`)
- **Models**: `[entity].py` (e.g., `interview.py`, `candidate.py`)
- **Tests**: `test_[module_name].py`

### **Environment Management**
- **Root `.env.example`**: Template for all services
- **Service-specific config**: `app/infrastructure/config.py`
- **Shared config**: Use `org_shared` package from `/shared/`

### **Database Integration**
- **Primary DB**: Supabase (see `/docs/db--state.md` for schema)
- **Caching**: Redis (for session management)
- **File Storage**: Supabase Storage (resumes, transcripts)

### **AI Service Integration**
```python
# Standard pattern for LLM services
from openai import OpenAI
from google.generativeai import GenerativeModel
import os

class EvaluationService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.gemini_model = GenerativeModel("gemini-2.5-pro")
    
    async def evaluate_interview(self, transcript: str) -> dict:
        # Implementation
        pass
```

### **Testing Requirements**
- **Unit tests**: Required for all service classes
- **Integration tests**: Required for API endpoints
- **Pipecat tests**: Use mock transport for speech services
- **Coverage**: Maintain >80% coverage (see `/services/evaluator/htmlcov/`)

## 🚫 IAgent-Specific Anti-Patterns

### Never Do:
- ❌ Mix Pipecat orchestration with FastAPI routes
- ❌ Hard-code API keys (use environment variables)
- ❌ Direct database access from routes (use service layer)
- ❌ Store sensitive data in transcripts
- ❌ Block event loops with synchronous LLM calls

### Always Split When:
- ❌ FastAPI route file handles multiple endpoints (>5 routes)
- ❌ Service class handles multiple AI providers
- ❌ Pipecat pipeline file exceeds 500 lines
- ❌ Configuration file mixes multiple service configs

## ✅ IAgent Code Templates

### **FastAPI Service Template**
```python
# services/[service]/app/services/[feature]_service.py
from typing import Optional, List
from supabase import create_client, Client
from ..infrastructure.config import Settings

class InterviewService:
    """
    Interview Service
    Handles interview lifecycle management
    """
    
    def __init__(self):
        settings = Settings()
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_ANON_KEY
        )
    
    async def create_interview(self, candidate_id: str, job_id: str) -> dict:
        """Create new interview session"""
        # Implementation
        pass
    
    async def get_interview_status(self, interview_id: str) -> Optional[dict]:
        """Get interview status"""
        # Implementation
        pass
```

### **FastAPI Route Template**
```python
# services/[service]/app/routes/[feature]_routes.py
from fastapi import APIRouter, Depends, HTTPException
from ..services.[feature]_service import [Feature]Service
from ..models.[feature] import [Feature]Request, [Feature]Response

router = APIRouter(prefix="/api/v1/[feature]", tags=["[feature]"])

def get_[feature]_service() -> [Feature]Service:
    return [Feature]Service()

@router.post("/", response_model=[Feature]Response)
async def create_[feature](
    request: [Feature]Request,
    service: [Feature]Service = Depends(get_[feature]_service)
):
    """Create new [feature]"""
    try:
        result = await service.create_[feature](request)
        return [Feature]Response(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{[feature]_id}", response_model=[Feature]Response) 
async def get_[feature](
    [feature]_id: str,
    service: [Feature]Service = Depends(get_[feature]_service)
):
    """Get [feature] by ID"""
    result = await service.get_[feature]([feature]_id)
    if not result:
        raise HTTPException(status_code=404, detail="[Feature] not found")
    return [Feature]Response(**result)
```

### **Pipecat Service Template**
```python
# services/speech/app/services/[feature]_pipeline.py
import asyncio
from loguru import logger
from pipecat.pipeline.pipeline import Pipeline
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService

class InterviewPipeline:
    """
    Interview Pipeline
    Manages real-time interview conversation
    """
    
    def __init__(self):
        self.stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))
        self.llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = ElevenLabsTTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
        
    async def create_pipeline(self, transport) -> Pipeline:
        """Create interview pipeline"""
        return Pipeline([
            transport.input(),
            self.stt,
            self.llm,
            self.tts,
            transport.output(),
        ])
    
    async def start_interview(self, interview_context: dict):
        """Start interview with context"""
        # Implementation
        pass
```

### **Test Template**
```python
# services/[service]/tests/test_[feature]_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.[feature]_service import [Feature]Service

class Test[Feature]Service:
    """
    Unit tests for [Feature]Service
    Tests: CRUD operations, error handling, business logic
    """
    
    def setup_method(self):
        """Setup before each test"""
        self.service = [Feature]Service()
    
    @pytest.mark.asyncio
    async def test_create_[feature]_success(self):
        """Test successful [feature] creation"""
        # Arrange
        test_data = {"name": "test", "value": "data"}
        
        # Act
        with patch.object(self.service.supabase, 'table') as mock_table:
            mock_table.return_value.insert.return_value.execute.return_value.data = [test_data]
            result = await self.service.create_[feature](test_data)
        
        # Assert
        assert result == test_data
        mock_table.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_[feature]_not_found(self):
        """Test [feature] not found scenario"""
        # Implementation
        pass
```

## 📝 Development Checklist

### **Before Starting Development:**
- [ ] Check current service architecture in `/docs/db--state.md`
- [ ] Verify Python environment: `C:/Projects/GitHub/IAgent/.venv/Scripts/python.exe`
- [ ] Review existing service patterns in `/services/[service]/`
- [ ] Check `.env.example` for required environment variables
- [ ] Understand Supabase schema and queue workflows

### **During Development:**
- [ ] Keep Python files under 500 lines (Pipecat: 600 max)
- [ ] Use `org_shared` package for common utilities
- [ ] Follow FastAPI async patterns
- [ ] Implement proper error handling with HTTPException
- [ ] Use Supabase client for database operations
- [ ] Write tests for new functionality
- [ ] Update service Dockerfile if adding dependencies

### **Code Review Questions:**
- [ ] Does this integrate properly with Supabase?
- [ ] Are API keys properly managed through environment variables?
- [ ] Does Pipecat integration follow async patterns?
- [ ] Are LLM calls properly error-handled?
- [ ] Is the service properly containerized?
- [ ] Are tests covering the new functionality?

## 🔧 IAgent-Specific Refactoring Triggers

### **When to Split a Service:**
1. **Service exceeds 400 lines**
2. **Handles multiple AI providers in one class**
3. **Mixes FastAPI routes with Pipecat orchestration** 
4. **Combines interview logic with evaluation logic**
5. **Single file handles both STT and TTS**

### **How to Split:**
1. **Identify AI provider boundaries** (OpenAI vs Gemini vs Deepgram)
2. **Separate pipeline creation from business logic**
3. **Extract common utilities to `/shared/`**
4. **Update service imports and dependencies**
5. **Test service boundaries with integration tests**

## 🎯 IAgent Success Metrics

### **Good Architecture Indicators:**
- ✅ Each service has single responsibility (interview vs evaluation vs speech)
- ✅ AI provider integrations are properly abstracted
- ✅ Pipecat pipelines are cleanly separated from REST APIs
- ✅ Supabase integration follows consistent patterns
- ✅ Environment variables are properly managed
- ✅ Tests cover both sync and async operations

### **Red Flags:**
- 🚨 Mixed AI providers in single service class
- 🚨 Pipecat and FastAPI mixed in same file
- 🚨 Hard-coded API keys or endpoints
- 🚨 Synchronous database calls in async endpoints
- 🚨 Missing error handling for external API calls

## 🔄 Migration Strategy

### **From Current State to Production:**
1. **Complete core service implementation**
2. **Add Docker Compose for local development**
3. **Implement comprehensive error handling**
4. **Add monitoring and logging standards**
5. **Create production environment configurations**
6. **Set up CI/CD pipeline for service deployment**

### **Future Monorepo Migration (Phase 2):**

When ready to extract shared components, follow this migration plan:

#### **Shared Component Extraction:**
```
shared/
├── infrastructure/
│   ├── supabase/                # Database utilities
│   │   ├── client.py           # From evaluator HTTP client
│   │   ├── services/           # Split from evaluator services.py
│   │   └── repositories/       # From evaluator repositories
│   ├── llm/                    # LLM abstractions
│   │   ├── providers/          # Extract from evaluator helpers.py
│   │   │   ├── openai_provider.py
│   │   │   ├── google_provider.py
│   │   │   └── openrouter_provider.py
│   │   └── evaluation/         # Evaluation utilities
│   └── config/                 # Shared configuration
└── domain/
    └── entities/               # Shared domain models
        ├── interview.py        # From evaluator
        ├── candidate.py
        └── evaluation.py
```

#### **Migration Steps:**
1. **Extract database utilities** from evaluator to `shared/infrastructure/supabase/`
2. **Extract LLM providers** from evaluator `helpers.py` to `shared/infrastructure/llm/`
3. **Move domain models** to `shared/domain/entities/`
4. **Update service imports** to use shared components
5. **Create workspace management** (poetry workspaces)

#### **Service Boundaries After Migration:**
- **Evaluator**: LLM evaluation workflows, score calculation
- **Speech**: Audio processing with Pipecat, STT/TTS
- **Core**: User management, interview scheduling
- **Content Generation**: Question generation, rubric creation

This migration preserves the working evaluator service while enabling code reuse across new services.

## 📖 Quick Reference

### **Decision Tree for IAgent:**
```
Is this related to real-time speech processing?
├── YES → Put in /services/speech/ with Pipecat
└── NO → Is this LLM evaluation logic?
    ├── YES → Put in /services/evaluator/
    └── NO → Is this user/interview management?
        ├── YES → Put in /services/core/
        └── NO → Is this cross-service functionality?
            ├── YES → Put in /shared/
            └── NO → Add to /api-gateway/
```

### **Service Ports:**
- **api-gateway**: 8000
- **core**: 8001  
- **speech**: 8002
- **evaluator**: 8005

### **Key Environment Variables:**
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `DEEPSEEK_API_KEY`
- `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`
- `SIMLI_API_KEY`, `SIMLI_FACE_ID`

---

## 💡 Remember
**"Each service should own its domain completely"** - Follow this principle for the IAgent microservices architecture.

**When in doubt about service boundaries, check the database schema in `/docs/db--state.md`** - the data model drives the service boundaries.