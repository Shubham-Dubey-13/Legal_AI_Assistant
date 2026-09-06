# ⚖️ LegalAI — Multi-Agent AI Legal Assistant for Indian Law

> **Production-Grade Full-Stack AI System** | Final-Year B.Tech Project  
> Built by **Shubham Dubey** | B.Tech CSE (AI/ML)

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://reactjs.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange?logo=google)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-red)](https://chromadb.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![GitHub](https://img.shields.io/badge/GitHub-Shubham--Dubey--13-black?logo=github)](https://github.com/Shubham-Dubey-13/Legal_AI_Assistant)

---

## 🎯 Problem Statement

- **47 million+** pending court cases in India
- Legal consultation costs ₹2,000–₹10,000/hour — unaffordable for 70%+ citizens
- Complex legal language inaccessible to common people
- No AI tool trained specifically on IPC → BNS 2023 transition, BNSS 2023, Indian Constitution
- Generic LLMs hallucinate section numbers, case names, and legal conclusions

---

## 💡 Solution

LegalAI is a **multi-agent AI legal workspace** that takes a user from:
**Question → Research → Evidence → Verification → Analysis → Draft → Cited Report**

Without switching tools. Without hallucinated citations. In the user's native language.

---

## 🏗️ Architecture

```
User Query (8 Indian Languages)
        │
        ▼
   FastAPI Backend  ←──── JWT Auth (bcrypt)
        │
        ▼
  Orchestrator Agent (Gemini 2.5 Flash)
        │
   ┌────┴──────────────────────────────────┐
   │                                       │
   ▼                                       ▼
Research Agent                    Retrieval Agent
 ├─ IPC/BNS section mapping         ├─ ChromaDB dense search
 ├─ Indian Kanoon lookup             ├─ BM25 sparse search
 └─ Case law identification         └─ Reciprocal Rank Fusion
                                        │
                                        ▼
                              Verification Agent
                               ├─ Section number validation
                               ├─ LLM self-critique
                               └─ Confidence scoring
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼             ▼
                   Summarization    Drafting      Citation
                     Agent           Agent          Agent
                          │
                          ▼
                   Memory Agent ──→ Conversation DB
                          │
                          ▼
              Final Response + Citations + Agent Trace
                  (React TypeScript Frontend)
```

---

## 🤖 Agent Details

| Agent | Technology | Responsibility |
|-------|-----------|----------------|
| **Orchestrator** | Gemini 2.5 Flash | Routes queries, classifies intent, synthesizes output |
| **Research** | LangChain + IPC/BNS Map | Identifies applicable sections, case law |
| **Retrieval** | ChromaDB + BM25 + RRF | Hybrid semantic + keyword search |
| **Verification** | Rule-based + LLM critique | Validates sections, computes confidence score |
| **Summarization** | Gemini 2.5 Flash | Condenses retrieved evidence, summarizes PDFs |
| **Drafting** | Template + LLM | Generates FIR, notice, petition, affidavit |
| **Citation** | Regex + SCC/AIR patterns | Formats Indian legal citations |
| **Memory** | SQLite + Context Manager | Persists conversation history per user |

---

## 🔍 RAG Pipeline

```
Legal PDF Upload
      │
      ▼
PyMuPDF Text Extraction
      │
      ▼  (if scanned)
Tesseract OCR (Hindi/English)
      │
      ▼
Section-Aware Chunking (512 tokens + 50 overlap)
      │
      ▼
Google Generative AI Embeddings (embedding-001)
      │
      ▼
ChromaDB Vector Store (cosine similarity)
      │
      ▼
Query → Hybrid Retrieval (Dense + BM25)
      │
      ▼
Reciprocal Rank Fusion (RRF merging)
      │
      ▼
Verification Agent (confidence scoring)
      │
      ▼
Gemini 2.5 Flash (grounded generation)
      │
      ▼
Citation Agent (SCC/AIR format)
      │
      ▼
Response + Source Citations + Agent Trace
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Gemini API Key ([Get free key](https://aistudio.google.com/app/apikey))

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your_key_here

# Start backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Full Stack with Docker
```bash
# Configure API keys
cp backend/.env.example backend/.env
# Edit backend/.env → add GOOGLE_API_KEY

# Start all services (PostgreSQL, Redis, ChromaDB, Backend, Frontend, Nginx)
docker-compose up --build

# Open http://localhost:80
```

### Seed Legal Corpus (optional, for ChromaDB retrieval)
```bash
docker-compose up chromadb -d    # Start ChromaDB first
python scripts/seed_legal_data.py
```

---

## 📁 Project Structure

```
Legal_AI_Assistant/
├── frontend/                      # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── pages/                 # 9 pages: Chat, Documents, Search, Drafts,
│   │   │                          #           Agents, Analytics, Prediction, Auth, Landing
│   │   ├── components/            # Sidebar, Header, common UI
│   │   ├── services/api.ts        # Axios client (90s timeout for LLM calls)
│   │   └── store/authStore.ts     # Zustand auth state
│   └── Dockerfile                 # Multi-stage: Node build → Nginx serve
│
├── backend/                       # FastAPI REST API
│   ├── app/
│   │   ├── api/v1/endpoints/      # auth, chat, documents, search, drafts,
│   │   │                          #   agents, analytics, evaluation, ws
│   │   ├── models/models.py       # SQLAlchemy: User, Conversation, Message,
│   │   │                          #             LegalDocument, LegalDraft, AgentLog
│   │   ├── core/security.py       # JWT + bcrypt (direct, no passlib bug)
│   │   └── core/config.py         # Settings: Gemini 2.5 Flash
│   └── Dockerfile                 # Python 3.11 + Tesseract OCR
│
├── ai_services/                   # AI/ML pipeline
│   ├── agents/                    # 8 specialized agents
│   │   ├── orchestrator.py        # Master coordinator
│   │   ├── research_agent.py      # IPC/BNS research (12K corpus map)
│   │   ├── retrieval_agent.py     # Hybrid BM25 + dense + RRF
│   │   ├── verification_agent.py  # Hallucination detection
│   │   ├── summarization_agent.py # Document + chunk summarization
│   │   ├── drafting_agent.py      # Legal document generation
│   │   ├── citation_agent.py      # SCC/AIR citation formatting
│   │   └── memory_agent.py        # Conversation context
│   ├── rag/
│   │   ├── document_processor.py  # Full PDF → ChromaDB pipeline
│   │   └── retriever.py           # HybridRetriever interface
│   ├── nlp/section_identifier.py  # IPC ↔ BNS section mapping
│   └── ml/judgment_predictor.py   # Outcome prediction (research component)
│
├── data/
│   ├── eval/eval_set.json         # 50 curated Q&A pairs for evaluation
│   └── seed/legal_corpus.json     # 60 Indian law entries for ChromaDB seeding
│
├── scripts/seed_legal_data.py     # Corpus seeding script
├── deployment/nginx/nginx.conf    # Reverse proxy config
├── docker-compose.yml             # PostgreSQL + Redis + ChromaDB + Nginx
└── README.md
```

---

## 📊 Evaluation Metrics

Run evaluation via API:
```bash
# Trigger evaluation run (10 questions, ~60 seconds)
curl -X POST http://localhost:8000/api/v1/evaluation/run?max_questions=10 \
     -H "Authorization: Bearer <token>"

# Get results
curl http://localhost:8000/api/v1/evaluation/metrics \
     -H "Authorization: Bearer <token>"
```

| Metric | Description | Target |
|--------|-------------|--------|
| **Section Recall** | % of expected IPC/BNS sections found in responses | > 70% |
| **Keyword Coverage** | % of expected legal keywords present | > 65% |
| **Abstain Rate** | % of off-topic queries that trigger abstain response | > 90% |
| **Avg Latency** | End-to-end response time | < 10 seconds |

**Evaluation Dataset**: 50 curated questions across criminal, constitutional, consumer, family, property, cyber, and labor law categories.

---

## 🔒 Security

- **Authentication**: JWT tokens (HS256, 30-minute expiry)
- **Password Policy**: Minimum 8 chars, 1 uppercase, 1 symbol — enforced frontend + backend
- **Password Hashing**: bcrypt (direct — avoids passlib 72-byte bug)
- **Document Isolation**: Every document/conversation query filtered by `user_id`
- **Rate Limiting**: Nginx rate limit 30 req/min on API endpoints
- **Input Sanitization**: File type/size validation on upload
- **Prompt Injection**: System prompt isolated from user text

---

## 🌍 Multi-Language Support

| Language | Code | LLM Instruction |
|----------|------|-----------------|
| English | `en` | Default |
| Hindi | `hi` | केवल हिंदी में उत्तर दें |
| Tamil | `ta` | தமிழில் மட்டும் பதிலளிக்கவும் |
| Telugu | `te` | తెలుగులో మాత్రమే సమాధానం ఇవ్వండి |
| Bengali | `bn` | শুধুমাত্র বাংলায় উত্তর দিন |
| Marathi | `mr` | फक्त मराठीत उत्तर द्या |
| Gujarati | `gu` | ફક્ત ગુજરાતીમાં જવાબ આપો |
| Punjabi | `pa` | ਸਿਰਫ਼ ਪੰਜਾਬੀ ਵਿੱਚ ਜਵਾਬ ਦਿਓ |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite, Zustand, Framer Motion |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy, Pydantic v2 |
| **Database** | SQLite (dev) / PostgreSQL (prod), ChromaDB (vectors) |
| **AI** | Google Gemini 2.5 Flash, LangChain, Google Embeddings |
| **Retrieval** | ChromaDB (dense), rank-bm25 (sparse), RRF merging |
| **Document AI** | PyMuPDF, pdfplumber, Tesseract OCR |
| **Auth** | JWT (python-jose), bcrypt |
| **Deployment** | Docker Compose, Nginx, Redis, Celery |
| **Cache/Queue** | Redis, FastAPI BackgroundTasks |

---

## 📋 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/login` | Login, get JWT token |
| `POST` | `/api/v1/chat/query` | Ask legal question (multi-agent) |
| `GET` | `/api/v1/chat/conversations` | List user conversations |
| `GET` | `/api/v1/chat/conversations/{id}/history` | Get message history |
| `POST` | `/api/v1/documents/upload` | Upload legal PDF |
| `GET` | `/api/v1/documents/` | List user documents |
| `GET` | `/api/v1/documents/{id}` | Get document analysis |
| `POST` | `/api/v1/search/caselaw` | Semantic case law search |
| `GET` | `/api/v1/search/ipc-sections` | Find IPC sections |
| `GET` | `/api/v1/search/bns-sections` | Find BNS 2023 sections |
| `POST` | `/api/v1/drafts/generate` | Generate legal draft |
| `GET` | `/api/v1/agents/status` | All 8 agents status |
| `GET` | `/api/v1/evaluation/metrics` | Retrieval/citation metrics |
| `POST` | `/api/v1/evaluation/run` | Run evaluation suite |
| `WS` | `/ws/chat/{conversation_id}` | Real-time streaming |

Interactive docs: `http://localhost:8000/docs`

---

## ⚠️ Limitations & Ethics

- **Not legal advice**: LegalAI provides legal information, not professional legal advice. Always consult a qualified advocate for specific legal matters.
- **Citation accuracy**: AI-generated citations should be verified against official sources (IndianKanoon, eCourts).
- **Judgment prediction**: The ML prediction module is a research component, not a reliable outcome predictor. Class imbalance and dataset shift affect accuracy.
- **Corpus coverage**: The knowledge base covers major Indian Acts but is not exhaustive. Recent amendments may not be reflected.
- **Language quality**: Non-English responses are generated by LLM translation and may contain errors.

For free legal aid: **NALSA Helpline 15100** (toll-free)

---

## 🗺️ Viva / Interview Preparation

**Key questions to prepare:**
1. Why RAG over relying only on LLM for legal research?
2. How does RRF (Reciprocal Rank Fusion) combine dense + sparse results?
3. What is the role of the Verification Agent — how does it reduce hallucinations?
4. How does the orchestrator decide which agent to invoke?
5. How do you handle scanned (image-only) PDFs?
6. How do you measure retrieval quality? (section recall, keyword coverage)
7. Why bcrypt directly instead of passlib? (72-byte bug)
8. How does the abstain mechanism work when evidence is insufficient?
9. What is the BNS 2023 and how does it differ from IPC 1860?
10. How would you scale this to 1 million documents?

---

## 📄 Research Paper Potential

**Hypothesis**: Multi-agent orchestration with hybrid RAG reduces hallucinated legal citations compared to single-LLM baselines on Indian legal Q&A.

**Datasets**: 50-question curated eval set (included), INLegalNLP, Indian Kanoon corpus

**Baselines**: Direct LLM (GPT-4o), Single-agent RAG, BM25-only retrieval

**Conferences**: ACL System Demo, EMNLP, IEEE ICAICT, Springer LNAI

---

## 📧 Contact

**Developer**: Shubham Dubey | B.Tech CSE (AI/ML)  
**GitHub**: [Shubham-Dubey-13/Legal_AI_Assistant](https://github.com/Shubham-Dubey-13/Legal_AI_Assistant)  
**Free Legal Aid**: NALSA Helpline — **15100**
