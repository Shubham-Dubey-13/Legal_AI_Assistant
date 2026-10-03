# Multi-Agent AI Legal Assistant for Indian Law
## Complete Project Blueprint & Implementation Guide

---

## Project Overview

**Problem Statement**: India has over 47 million pending court cases. Legal help is expensive (₹2,000–₹10,000/hour), inaccessible in regional languages, and requires navigating a complex maze of IPC, BNS, CrPC, Constitution, and thousands of court judgments. Common citizens cannot understand their legal rights.

**Solution**: A production-grade Multi-Agent AI Legal Assistant that democratizes access to Indian legal knowledge using state-of-the-art Agentic AI, RAG pipelines, and Generative AI.

---

## Proposed Changes

### Component 1: Frontend (React + Vite)
#### [NEW] Legal Assistant Web App
- Modern dark-theme UI with glassmorphism
- Multi-tab interface: Chat, Document Upload, Case Search, Draft Generator, Analytics Dashboard
- Real-time streaming responses with agent status indicators
- Voice input/output interface
- PDF viewer with annotation highlights
- Multi-language selector (Hindi, Tamil, Telugu, Bengali, Marathi)
- Citation panel, judgment predictor UI, legal draft editor

### Component 2: Backend (FastAPI + Python)
#### [NEW] API Gateway & Orchestration Layer
- RESTful + WebSocket APIs
- JWT Authentication
- Rate limiting & caching (Redis)
- File upload handling (PDF, DOCX)
- Session & conversation management
- Celery task queue for async agent jobs

### Component 3: Agentic AI System (LangChain + LangGraph)
#### [NEW] Multi-Agent Orchestration
- **Orchestrator Agent** — Master coordinator using LangGraph StateGraph
- **Research Agent** — Autonomous legal research from web & databases
- **Retrieval Agent** — RAG-powered case law and statute retrieval
- **Verification Agent** — Hallucination checking & citation validation
- **Summarization Agent** — PDF parsing and legal document summarization
- **Drafting Agent** — Legal document generation (FIR, petition, notice, affidavit)
- **Citation Agent** — SCC, AIR, Supreme Court citation generation
- **Memory Agent** — Long-term conversation memory with user legal profile

### Component 4: RAG Pipeline
#### [NEW] Vector Search & Embeddings
- ChromaDB / Pinecone vector store
- Legal text chunking strategy (section-aware)
- OpenAI/Cohere embeddings
- Hybrid search (dense + sparse BM25)
- Re-ranking with cross-encoders
- Context compression

### Component 5: ML Models
#### [NEW] Specialized Legal ML
- IPC/BNS section classifier (fine-tuned BERT/Legal-BERT)
- Judgment outcome predictor (XGBoost + BERT features)
- Named Entity Recognition for legal entities
- Legal text similarity model

### Component 6: Database Layer
#### [NEW] Multi-Database Architecture
- PostgreSQL — User profiles, case metadata, chat history
- ChromaDB — Vector embeddings for semantic search
- Redis — Caching, session management, rate limiting
- MongoDB — Unstructured legal documents, drafts

---

## Open Questions

> [!IMPORTANT]
> **LLM Provider**: Should we use OpenAI GPT-4o, Google Gemini, or open-source Mistral/Llama? For a student project, OpenAI with a free-tier key works. We'll architect for provider-agnostic switching.

> [!NOTE]
> **Dataset**: We'll use freely available Indian court judgment datasets from Indian Kanoon API, eCourts, and Kaggle datasets.

---

## Verification Plan
- Run all agents in simulation mode with mock data
- Test PDF parsing with sample legal documents
- Verify RAG retrieval accuracy with test queries
- Browser test the complete UI flow
