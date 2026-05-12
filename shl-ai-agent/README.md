# SHL Conversational Assessment Recommender

A stateless conversational RAG API that recommends relevant SHL assessments using semantic retrieval and grounded LLM responses.

The system supports:

- assessment recommendation
- clarification questions
- recommendation refinement
- assessment comparison
- prompt-injection refusal

All recommendations are grounded strictly in the local SHL catalog dataset.

---

# Features

- FastAPI backend with strict Pydantic schemas
- Hybrid retrieval using FAISS + RapidFuzz
- Semantic embeddings with sentence-transformers
- Stateless conversation handling
- Catalog-grounded recommendation generation
- Prompt injection and off-topic refusal handling
- Automated API and behavior tests
- Render-ready deployment configuration

---

# Project Structure

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

scripts/
├── preprocess.py
└── build_index.py

tests/
└── test_api.py
```

---

# Architecture Overview

The application follows a Retrieval-Augmented Generation (RAG) architecture.

## Retrieval Pipeline

1. Catalog preprocessing generates searchable text fields.
2. Sentence-transformer embeddings are generated for catalog entries.
3. FAISS performs semantic similarity search.
4. RapidFuzz performs keyword-based scoring.
5. Hybrid ranking combines semantic and lexical relevance.

## Conversation Flow

The API remains fully stateless.

Each `/chat` request includes the required conversation history for the current turn.

Supported conversational behaviors:

- clarification
- recommendation
- refinement
- comparison
- refusal handling

---

# Setup

## 1. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key
```

---

# Build Retrieval Index

```powershell
python scripts/preprocess.py
python scripts/build_index.py
```

This generates:

- processed catalog data
- FAISS vector index
- retrieval metadata

---

# Run Locally

```powershell
uvicorn app.main:app --reload --port 8080
```

API:

```text
http://127.0.0.1:8080
```

Swagger Docs:

```text
http://127.0.0.1:8080/docs
```

Health Check:

```text
http://127.0.0.1:8080/health
```

---

# API

## POST `/chat`

### Request

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

### Response

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

# Environment Variables

| Variable               | Description             |
| ---------------------- | ----------------------- |
| GEMINI_API_KEY         | Gemini API key          |
| GEMINI_MODEL           | Gemini model name       |
| CATALOG_PATH           | Raw catalog path        |
| PROCESSED_CATALOG_PATH | Processed catalog path  |
| FAISS_INDEX_PATH       | FAISS index path        |
| INDEX_METADATA_PATH    | Retrieval metadata path |
| EMBEDDING_MODEL        | Embedding model         |
| LOG_LEVEL              | Logging level           |

---

# Testing

Run tests:

```powershell
pytest
```

Tests cover:

- schema validation
- grounded recommendations
- clarification flow
- refinement flow
- comparison behavior
- refusal handling

---

# Deployment

The repository includes `render.yaml` for deployment on Render.

## Build Command

```bash
pip install -r requirements.txt && python scripts/preprocess.py && python scripts/build_index.py
```

## Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

Set `GEMINI_API_KEY` in the Render dashboard environment variables.

---

# Evaluation Strategy

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
