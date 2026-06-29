# ⚖️ Multi-Agent AI Legal Assistant for Indian Law

> **Enterprise-Grade Legal AI System**  
> A production-grade, multi-agent AI system that democratizes access to Indian legal knowledge using Agentic AI, RAG, LangChain, LangGraph, Vector Databases, and Generative AI.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-purple)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-orange)](https://langchain-ai.github.io/langgraph)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-red)](https://chromadb.com)

---

## 🏆 Project Highlights

| Feature | Technology |
|---------|-----------|
| Multi-Agent Orchestration | LangGraph StateGraph |
| RAG Pipeline | ChromaDB + Hybrid Search |
| LLM Backend | GPT-4o / Gemini Pro |
| Legal NLP | Legal-BERT Fine-tuned |
| Frontend | React + TypeScript |
| Backend API | FastAPI + WebSockets |
| Deployment | Docker + AWS ECS |

---

## 🎯 Problem Statement

- **47 million+** pending court cases in India
- Legal help costs ₹2,000–₹10,000 per hour
- 70%+ population cannot afford legal consultation
- Legal documents in complex English inaccessible to common people
- No AI tool specifically trained on Indian law (IPC, BNS, CrPC, Constitution)

---

## 💡 Solution Architecture

```
User Query
    ↓
Orchestrator Agent (LangGraph)
    ↓
┌───────────────────────────────────────┐
│  Research  │ Retrieval │ Verification │
│   Agent    │   Agent   │    Agent     │
├───────────────────────────────────────┤
│ Summarize  │  Draft    │  Citation    │
│   Agent    │  Agent    │   Agent     │
└───────────────────────────────────────┘
    ↓
RAG Pipeline (ChromaDB + Hybrid Search)
    ↓
Legal Knowledge Base (Indian Law Corpus)
    ↓
Final Response + Citations + Draft
```

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/legal-ai-assistant
cd legal-ai-assistant

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload

# Frontend Setup
cd ../frontend
npm install
npm run dev

# AI Services
cd ../ai-services
pip install -r requirements.txt
python -m agents.orchestrator
```

---

## 📁 Project Structure

```
legal-ai-assistant/
├── frontend/                    # React + TypeScript UI
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route pages
│   │   ├── hooks/              # Custom React hooks
│   │   ├── store/              # Zustand state management
│   │   ├── services/           # API clients
│   │   └── utils/              # Helper functions
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── middleware/        # Auth, logging, CORS
├── ai-services/                # AI/ML pipeline
│   ├── agents/                # LangGraph agents
│   ├── rag/                   # RAG pipeline
│   ├── ml/                    # ML models
│   ├── nlp/                   # NLP processing
│   └── tools/                 # Agent tools
├── deployment/                 # Docker + Kubernetes
│   ├── docker-compose.yml
│   └── kubernetes/
└── docs/                      # Documentation
```

---

## 🤖 AI Agents

### 1. Orchestrator Agent
- Master coordinator using LangGraph StateGraph
- Routes queries to appropriate specialist agents
- Manages parallel and sequential agent execution
- Aggregates and synthesizes multi-agent outputs

### 2. Research Agent
- Autonomous web search for latest legal updates
- Scrapes Indian Kanoon, eCourts portal
- Summarizes recent amendments (BNS 2023, BNSS 2023)

### 3. Retrieval Agent  
- RAG-powered retrieval from legal knowledge base
- Hybrid search: semantic (dense) + BM25 (sparse)
- Cross-encoder re-ranking for relevance
- Returns top-k legally relevant chunks

### 4. Verification Agent
- Hallucination detection and fact-checking
- Citation validation against real case law
- Confidence scoring for AI responses

### 5. Summarization Agent
- Legal PDF parsing and chunking
- Extractive + abstractive summarization
- Key points, parties, and judgment extraction

### 6. Drafting Agent
- Generates FIR, legal notices, petitions, affidavits
- Template-based with AI personalization
- Section-aware legal language generation

### 7. Citation Agent
- SCC, AIR, Supreme Court citation formatting
- Automated citation extraction from summaries
- Bluebook and Indian citation standards

### 8. Memory Agent
- Long-term conversation history
- User legal profile building
- Context-aware follow-up handling

---

## 🧠 RAG Pipeline

```
Legal Document Upload
        ↓
PDF Parsing (PyMuPDF/pdfplumber)
        ↓  
Text Chunking (Section-aware, 512 tokens)
        ↓
Embedding Generation (text-embedding-3-large)
        ↓
ChromaDB Vector Store
        ↓
Query → Hybrid Search (Dense + BM25)
        ↓
Cross-Encoder Re-ranking
        ↓
Context Compression
        ↓
LLM Response Generation
        ↓
Citation Injection
```

---

## 🔬 ML Models

| Model | Task | Framework |
|-------|------|-----------|
| Legal-BERT Fine-tuned | IPC/BNS Section Classification | HuggingFace |
| XGBoost + BERT Features | Judgment Outcome Prediction | Scikit-learn |
| spaCy + Custom NER | Legal Entity Recognition | spaCy |
| Sentence-BERT | Semantic Similarity | HuggingFace |
| Whisper | Speech-to-Text | OpenAI |

---

## 📊 Tech Stack

### Frontend
- React 18 + TypeScript + Vite
- Zustand (state management)
- React Query (server state)
- Socket.io-client (real-time)
- PDF.js (document viewer)
- Framer Motion (animations)

### Backend
- FastAPI + Python 3.11
- PostgreSQL + SQLAlchemy
- Redis (caching/sessions)
- Celery (async tasks)
- WebSockets (streaming)

### AI/ML
- LangChain 0.2+
- LangGraph (agent orchestration)
- ChromaDB (vector database)
- OpenAI GPT-4o / Gemini Pro
- HuggingFace Transformers
- spaCy / NLTK

### Deployment
- Docker + Docker Compose
- AWS ECS / EC2
- Nginx (reverse proxy)
- GitHub Actions (CI/CD)

---

## 📈 Resume Value

**Skills Demonstrated:**
- Agentic AI systems with LangGraph
- RAG pipeline design and optimization
- LLM prompt engineering
- Vector database operations
- Full-stack development
- System design at scale
- MLOps and deployment

**Target Companies:** Google DeepMind, Microsoft AI, Amazon AI, Deloitte AI, Accenture AI, Indian legal tech startups (Vakil Tech, MyAdvo, LawSikho)

---

## 📄 Research Paper Potential

This project has direct potential for:
- IEEE ICAICT / ICCIT conference papers
- ACL/EMNLP system demo papers
- Springer LNAI volume publication
- arXiv preprint submission

**Novelty**: First multi-agent system specifically designed for Indian legal corpus with BNS/BNSS 2023 support.

---

## 🗺️ Implementation Roadmap

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Phase 1 | Week 1-2 | Core RAG pipeline + Basic chat |
| Phase 2 | Week 3-4 | Multi-agent system + Document upload |
| Phase 3 | Week 5-6 | ML models + Prediction features |
| Phase 4 | Week 7-8 | Advanced features + Voice |
| Phase 5 | Week 9-10 | UI polish + Testing |
| Phase 6 | Week 11-12 | Deployment + Documentation |

---

## 📧 Contact

**Student**: [Your Name] | B.Tech CSE AIML | Batch 2021-25  
**Guide**: [Guide Name] | [Department] | [College]

