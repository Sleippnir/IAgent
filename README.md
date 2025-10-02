# IAgent - AI Interview Platform

**Status:** ✅ Active Development | **Current Branch:** `another-supabase`

## 🎯 Quick Start for New Sessions

### **Essential Documentation**
1. **[/docs/work-guidelines.md](./docs/work-guidelines.md)** - ⭐ **START HERE** - Complete development guidelines & architecture
2. **[/docs/db--state.md](./docs/db--state.md)** - Database schema & workflows
3. **[/services/evaluator/docs/status.md](./services/evaluator/docs/status.md)** - Production-ready LLM evaluation service

### **Current Architecture**
```
IAgent/                           # AI interview platform
├── docs/                         # Project documentation
│   ├── work-guidelines.md       # ⭐ Development standards & architecture
│   └── db--state.md             # Database schema & Supabase workflows
├── services/                     # Microservices
│   ├── evaluator/               # ✅ PRODUCTION READY - LLM evaluation
│   ├── speech/                  # STT/TTS with Pipecat
│   └── core/                    # User management & business logic
├── api-gateway/                 # FastAPI gateway (Port 8000)
├── frontend/                    # Web interface
├── shared/                      # Common utilities (org_shared package)
└── supabase/                    # Database backend
```

## 🔧 Environment Setup

**Python Environment:** `C:/Projects/GitHub/IAgent/.venv/Scripts/python.exe`

**Key Environment Variables:**
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `DEEPSEEK_API_KEY`
- `DEEPGRAM_API_KEY`, `ELEVENLABS_API_KEY`, `SIMLI_API_KEY`

## 📊 Service Status

| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **evaluator** | 8005 | ✅ Production Ready | LLM-based interview evaluation |
| **api-gateway** | 8000 | 🔧 Functional | Request routing & authentication |
| **speech** | 8002 | 🔧 Development | Pipecat STT/TTS integration |
| **core** | 8001 | ⚠️ Incomplete | User management & workflows |

## 🎯 Current Focus Areas

1. **Core service completion** - User management & interview workflows
2. **Docker Compose setup** - Multi-service orchestration
3. **Frontend integration** - UI/API connectivity
4. **Production deployment** - Environment & monitoring setup

## 📖 Architecture Patterns

- **Microservices**: Domain-driven service boundaries
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **AI Integration**: Multi-provider LLM support (OpenAI, Gemini, DeepSeek)
- **Real-time**: Pipecat framework for speech processing
- **Testing**: >80% coverage on evaluator service

---

💡 **For LLM Agents:** Start with `/docs/work-guidelines.md` for complete context, then check service-specific documentation as needed.