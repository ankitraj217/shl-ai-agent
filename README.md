# SHL Conversational Assessment Recommender

A production-ready, single-service FastAPI application with a React recruiter copilot frontend for recommending SHL assessments from the local catalog only.

The system supports:

- SHL assessment recommendations
- clarification questions
- recommendation refinement
- catalog-grounded assessment comparison
- prompt-injection and off-topic refusal
- React + TypeScript frontend served by FastAPI

All recommendations are grounded strictly in `data/catalog.json`.

---

## Features

- FastAPI backend with strict Pydantic schemas
- Hybrid retrieval using FAISS + RapidFuzz
- Semantic embeddings with sentence-transformers
- Stateless conversation handling
- Catalog-grounded recommendation generation
- Prompt injection and off-topic refusal handling
- Automated API and behavior tests
- Render-ready deployment configuration

---

## Architecture Overview

The application follows a Retrieval-Augmented Generation (RAG) architecture.

### Retrieval Pipeline

1. Catalog preprocessing generates searchable text fields.
2. Sentence-transformer embeddings are generated for catalog entries.
3. FAISS performs semantic similarity search.
4. RapidFuzz performs keyword-based scoring.
5. Hybrid ranking combines semantic and lexical relevance.

### Conversation Flow

The API remains fully stateless.

Each `/chat` request includes the required conversation history for the current turn.

Supported conversational behaviors:

- clarification
- recommendation
- refinement
- comparison
- refusal handling

Frontend serving:

- React + TypeScript + Vite builds into `frontend/dist`.
- FastAPI serves `/` as the React app.
- FastAPI serves `/assets/*` as compiled Vite assets.
- Unknown non-API GET routes return `index.html` for SPA routing.
- `/chat`, `/health`, `/docs`, and `/openapi.json` continue to work normally.

---

## Project Structure

```text
app/
├── models/         # Request and response schemas
├── prompts/        # Prompt templates
├── routes/         # API endpoints
├── services/       # Retrieval and conversation logic
├── utils/          # Shared utilities
└── main.py         # FastAPI entrypoint

data/
├── catalog.json
├── processed_catalog.json
├── faiss.index
└── index_metadata.json

frontend/
└── src/
    ├── components/
    ├── pages/
    ├── services/
    ├── types/
    ├── App.tsx
    └── main.tsx

scripts/
├── preprocess.py
└── build_index.py

tests/
└── test_api.py
```

---

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set your Gemini key in `.env`:

```env
GEMINI_API_KEY=your_api_key
```

---

## Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

---

## Build

Build the React frontend:

```powershell
cd frontend
npm run build
cd ..
```

Build retrieval artifacts:

```powershell
python scripts/preprocess.py
python scripts/build_index.py
```

---

## Run Locally

Production-like single service:

```powershell
uvicorn app.main:app --reload --port 8080
```

Open:

```text
http://127.0.0.1:8080/
```

API/docs:

```text
http://127.0.0.1:8080/chat
http://127.0.0.1:8080/health
http://127.0.0.1:8080/docs
```

Frontend development server:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite dev server proxies `/chat` and `/health` to `http://127.0.0.1:8080`, so development does not require CORS.

---

## API

### POST `/chat`

Request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a mid-level Java developer with communication skills"
    }
  ]
}
```

Response:

```json
{
  "reply": "Recommended assessments...",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/...",
      "test_type": "Knowledge & Skills"
    }
  ],
  "end_of_conversation": false
}
```

---

## Environment Variables

| Variable                 | Description             |
| ------------------------ | ----------------------- |
| `GEMINI_API_KEY`         | Gemini API key          |
| `GEMINI_MODEL`           | Gemini model name       |
| `CATALOG_PATH`           | Raw catalog path        |
| `PROCESSED_CATALOG_PATH` | Processed catalog path  |
| `FAISS_INDEX_PATH`       | FAISS index path        |
| `INDEX_METADATA_PATH`    | Retrieval metadata path |
| `EMBEDDING_MODEL`        | Embedding model         |
| `LOG_LEVEL`              | Logging level           |

---

## Testing

```powershell
pytest
```

Tests cover:

- health checks
- schema validation
- grounded recommendations
- clarification flow
- refinement flow
- comparison behavior
- refusal handling

## Render Deployment

This project deploys as one Render web service. FastAPI serves both the React frontend and API from the same host/domain.

Build command:

```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && python scripts/preprocess.py && python scripts/build_index.py
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Set `GEMINI_API_KEY` in the Render dashboard. The deployed app exposes:

```text
https://my-app.onrender.com/
https://my-app.onrender.com/chat
https://my-app.onrender.com/health
https://my-app.onrender.com/docs
```

---

## Evaluation Strategy

Evaluate with vague recruiter queries, technical hiring prompts, refinement turns, comparison requests, and prompt-injection attempts. Check that recommendations always use catalog URLs, clarification/refusal turns return an empty recommendation list, and recommendation turns return 1-10 relevant SHL assessments.

The system was evaluated using:

- vague recruiter queries
- technical hiring requests
- refinement conversations
- comparison prompts
- prompt injection attempts

Evaluation focused on:

- grounded recommendations
- retrieval relevance
- schema compliance
- refusal correctness
- conversational consistency
