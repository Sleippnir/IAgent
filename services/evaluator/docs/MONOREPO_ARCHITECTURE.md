# IAgent Future Monorepo Migration Strategy

**Date:** October 2, 2025  
**Current Service:** Evaluator (Production Ready)  
**Purpose:** Future scaling plan for additional services

> **Note:** This document outlines future migration steps. Current evaluator service is production-ready and functional. Detailed current architecture is in `/docs/work-guidelines.md`.

## 🎯 **When to Migrate to Monorepo**

Migrate when you need to add additional services that would benefit from shared components:
- **Speech Service** (STT/TTS processing)
- **Content Generation Service** (Question/rubric generation)  
- **Scheduler Service** (Interview scheduling)
- **Analytics Service** (Reporting and insights)

## 🔄 **Migration Plan**

### **Phase 1: Extract Shared Components (Evaluator → Shared)**

Extract these components from the current evaluator service:

**1. Database Utilities → `shared/infrastructure/supabase/`**
- `app/infrastructure/persistence/supabase/client.py` → `shared/infrastructure/supabase/client.py`
- `app/infrastructure/persistence/supabase/services.py` → Split into `shared/infrastructure/supabase/services/`
- `app/infrastructure/persistence/supabase/*_repository.py` → `shared/infrastructure/supabase/repositories/`

**2. Domain Models → `shared/domain/entities/`**
- `app/domain/entities/interview.py` → `shared/domain/entities/interview.py`
- Create `shared/domain/entities/evaluation.py`, `transcript.py`, `candidate.py`

**3. LLM Abstractions → `shared/infrastructure/llm/`**
- Extract provider logic from `app/helpers.py` into:
  - `shared/infrastructure/llm/providers/openai_provider.py`
  - `shared/infrastructure/llm/providers/google_provider.py`
  - `shared/infrastructure/llm/providers/openrouter_provider.py`
- Extract evaluation utilities:
  - `shared/infrastructure/llm/evaluation/score_extractor.py`
  - `shared/infrastructure/llm/evaluation/transcript_generator.py`

**4. Configuration → `shared/infrastructure/config/`**
- `app/infrastructure/config.py` → `shared/infrastructure/config/settings.py`

### **Phase 2: Create New Services**

Once shared components are extracted, new services can leverage them:

**Speech Service:**
```python
# Uses shared infrastructure
from shared.infrastructure.supabase import TranscriptService
from shared.domain.entities import Interview
from shared.infrastructure.config import Settings
```

**Content Generation Service:**
```python
# Uses shared LLM providers
from shared.infrastructure.llm.providers import OpenAIProvider
from shared.domain.entities import Interview
```

### **Phase 3: Workspace Management**

Set up Python workspace management:

```toml
# Root pyproject.toml
[tool.poetry]
name = "iagent"
packages = [
    {include = "shared"},
    {include = "services/evaluator/app", from = "services/evaluator"},
    {include = "services/speech/app", from = "services/speech"},
]

[tool.poetry.dependencies]
python = "^3.12"
shared = {path = "./shared", develop = true}
```

## 🎯 **Service Boundaries After Migration**

- **Evaluator Service**: LLM evaluation workflows, score calculation, evaluation reports
- **Speech Service**: Real-time audio processing, STT/TTS, Pipecat orchestration  
- **Core Service**: User management, interview scheduling, business logic
- **Content Generation**: Question generation, rubric creation, content personalization

## � **Migration Checklist**

- [ ] Complete current service implementations first
- [ ] Extract shared Supabase utilities to `shared/infrastructure/supabase/`
- [ ] Extract shared domain models to `shared/domain/entities/`
- [ ] Extract LLM abstractions to `shared/infrastructure/llm/`
- [ ] Update evaluator service imports to use shared components
- [ ] Create workspace management configuration
- [ ] Set up shared component documentation
- [ ] Update CI/CD for workspace management

---

**Recommendation:** Complete the current microservices architecture first, then migrate to monorepo when adding the 3rd or 4th service. The current evaluator service provides an excellent foundation for shared component extraction.