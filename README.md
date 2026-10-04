# CODEBASE ARCHAEOLOGIST
> **"The Google Maps for an Unfamiliar Codebase"**

An AI-powered codebase understanding, architecture visualizer, impact analyzer, and developer onboarding platform.

---

## 🌟 Vision & Overview

When developers join a new project or audit an open-source repository, understanding how files connect, how features execute across layers, and what will break if a data model changes takes hours or days of manual code reading.

**Codebase Archaeologist** ingests software repositories (via GitHub URL or ZIP upload) and transforms them into an **interactive knowledge map**.

Unlike generic LLM chat interfaces that guess blindly, Codebase Archaeologist uses a **Graph-First Hybrid Architecture**:
- **Deterministic Static Analysis**: Tree-sitter AST parsing, NetworkX graph modeling, file tree scanners, and Git metadata provide 100% factual baseline truths.
- **Grounded LLM Intelligence**: Gemini/Claude/OpenAI models provide natural-language Q&A, onboarding summaries, and feature explanations anchored strictly in retrieved file lines and symbols.

---

## 🏗️ Architecture Overview

```
                          ┌──────────────────────────┐
                          │   Next.js 14 Frontend    │
                          │ React Flow + Tailwind    │
                          └─────────────┬────────────┘
                                        │ HTTP REST
                                        ▼
                          ┌──────────────────────────┐
                          │   FastAPI Python Server  │
                          └──────┬────────────┬──────┘
                                 │            │
            ┌────────────────────┘            └───────────────────┐
            ▼                                                     ▼
┌──────────────────────────┐                             ┌───────────────────┐
│ File Scanner & AST Parser│                             │ NetworkX & Graph  │
│ Tree-sitter JS/TS/TSX    │                             │ Impact Analyzer   │
└───────────┬──────────────┘                             └────────┬──────────┘
            │                                                     │
            └────────────────────┬────────────────────────────────┘
                                 ▼
                      ┌──────────────────────┐
                      │ PostgreSQL / SQLite  │
                      └──────────────────────┘
```

---

## ✨ Key Features

1. **Ingestion Engine**: Ingest GitHub repositories via URL or ZIP archives securely with path traversal protection and size limits.
2. **Grounded Repository Overview**: Automatic extraction of project purpose, main objectives, stack badges, entry points, major modules, and database schema.
3. **Interactive React Flow Architecture Map**: Node filtering, minimap, search, click-to-inspect source code previews, caller/callee counts.
4. **Interactive Feature Flow Tracer ("Trace This")**: Traces execution path across 5 layers: `Frontend Component → API Call → Backend Route → Controller/Service → Database Entity`.
5. **Graph-Based Impact Analysis ("What breaks if I change something?")**: Reverse dependency graph traversal identifying all affected files, components, routes, and models before making a change.
6. **Natural Language AI Q&A ("Ask Codebase")**: Grounded search providing answers with exact `file:line` evidence citations and confidence indicators.
7. **Developer Onboarding & Project Notes**: Auto-generates structured markdown onboarding documentation with copy and export controls (`.md`, `.txt`).
8. **Git Evolution Timeline**: Chronological milestone view extracting commit messages, authors, dates, and diff stats.
9. **5-Minute Guided Repository Tour**: Interactive step-by-step onboarding wizard introducing the codebase.

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, `@xyflow/react` (React Flow), Lucide Icons, Framer Motion
- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, NetworkX, GitPython
- **AST Code Analysis**: Tree-sitter (`tree-sitter`, `tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-language-pack`)
- **Database**: PostgreSQL (Docker / Production), SQLite (Zero-config local fallback)
- **AI Integration**: Google Gemini (`google-genai`), OpenAI, with deterministic offline fallback mode
- **DevOps**: Docker, Docker Compose

---

## 📁 Repository Structure

```
codebase-archaeologist/
├── frontend/                 # Next.js 14 React Flow Frontend
│   ├── app/                  # App Router pages and layout
│   ├── components/           # Navbar, Architecture map, Trace, Impact, Notes
│   ├── services/             # REST API client
│   └── package.json
├── backend/                  # FastAPI Python Backend
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   ├── core/             # Configuration & settings
│   │   ├── db/               # Session & SQLAlchemy engine
│   │   ├── models/           # DB schema entities
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── parser/           # File scanner & Tree-sitter AST parser
│   │   ├── graph/            # NetworkX graph builder & impact analyzer
│   │   ├── git/              # GitPython history analyzer
│   │   ├── ai/               # Grounded AIService
│   │   └── main.py           # FastAPI entry point
│   ├── tests/                # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml        # Docker composition for frontend, backend, postgres
├── .env.example
└── README.md
```

---

## 🚀 Quickstart & Local Setup

### Option 1: Docker Compose (Recommended)

1. Clone the repository and copy `.env.example`:
```bash
cp .env.example .env
```

2. Run Docker Compose:
```bash
docker compose up --build
```

3. Open your browser:
- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI Backend Swagger Specs**: `http://localhost:8000/api/openapi.json`

---

### Option 2: Local Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m pytest # Run backend tests
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

Run the automated backend test suite:
```bash
cd backend
python -m pytest
```

---

## 🏆 Demo Repository (CivicFix)

Codebase Archaeologist includes an instant demo seed button for **CivicFix**.
Click **"Demo: CivicFix"** in the top navigation bar to parse, build the graph, and explore architecture maps instantly!
