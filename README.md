# Nouvelair Knowledge Platform

> Internal knowledge-management platform with a Retrieval-Augmented Generation (RAG) assistant, developed during my summer 2026 internship at Nouvelair.

## Overview

The project centralizes internal knowledge resources and makes them easier to find through both traditional resource management and a conversational assistant.

Instead of relying only on document titles or keywords, the assistant retrieves relevant passages from indexed company resources, builds a grounded context, and generates an answer while keeping citations to the source documents for traceability.

## Main features

- Knowledge-resource management: PDF, DOCX, TXT, Markdown and text content
- Resource categories, search, preview and download
- Role-based access for platform users
- JWT authentication
- Automatic document extraction, chunking and indexing
- Conversational RAG assistant with persisted sessions and message history
- Hybrid retrieval combining similarity, keyword overlap and title relevance
- Source citations attached to generated answers
- Multi-provider LLM support with fallback behavior
- Re-indexing and removal of indexed content when resources change

## RAG pipeline

```text
Knowledge resources
       |
       v
PDF / DOCX / TXT / MD
       |
       v
Text extraction
       |
       v
Chunking + overlap
       |
       v
Local 384-dimensional hashing embeddings
       |
       v
JSON-backed local index
       |
       v
Hybrid retrieval
(cosine similarity + keywords + title relevance)
       |
       v
Top relevant passages
       |
       v
Context construction
       |
       v
Gemini / Groq / OpenAI
       |
       v
Grounded answer + source citations
```

The lightweight local index was chosen to keep the internship prototype portable and easy to run without a native vector-database dependency. The retrieval layer still follows the core RAG workflow: **extract -> chunk -> index -> retrieve -> generate -> cite**.

## Architecture

```text
+------------------------+
|      Angular 19        |
|       Frontend         |
+-----------+------------+
            |
          REST API
            |
+-----------v------------+
|        FastAPI         |
|        Backend         |
+------+----------+------+
       |          |
       v          v
    MySQL      RAG Engine
                  |
          Document extraction
                  |
              Indexing
                  |
          Hybrid retrieval
                  |
             LLM layer
                  |
         Answer + citations
```

## Technology stack

| Area | Technologies |
| --- | --- |
| Frontend | Angular 19, TypeScript, RxJS |
| Backend | Python, FastAPI, Pydantic |
| Persistence | MySQL, SQLAlchemy |
| Authentication | JWT / OAuth2 password flow |
| Document processing | PyPDF, PyMuPDF, python-docx |
| RAG | Chunking, local hashing embeddings, cosine similarity, keyword/title ranking |
| LLM integration | Google Gemini, Groq, OpenAI |
| API | REST |

## Authentication and roles

The backend uses JWT-based authentication. Protected endpoints resolve the current user from the access token, while resource-management operations can be restricted according to role.

For example, knowledge-resource creation and indexing are limited to authorized roles, while authenticated users can consult resources and use the assistant.

## Knowledge-resource lifecycle

When a resource is uploaded:

1. The file and its metadata are stored.
2. Text is extracted from the resource.
3. The text is split into overlapping chunks.
4. Each chunk is indexed in the local retrieval store.
5. The resource is marked as indexed.
6. Questions can retrieve the most relevant chunks.
7. Answers and their citations are stored for traceability.

Updating a resource triggers re-indexing, while deleting it also removes its indexed chunks and associated citations.

## Assistant behavior

For each question, the assistant:

1. Retrieves relevant passages using the full question and a keyword-oriented variant.
2. Filters low-relevance passages.
3. Builds a context exclusively from the retrieved knowledge.
4. Uses the configured LLM provider to generate the answer.
5. Returns the answer with the supporting resources/passages.
6. Stores the conversation and citations.

The application supports Gemini as a primary provider, Groq and OpenAI as alternatives, and a local extractive fallback when an external LLM is unavailable.

## Project structure

```text
nouvelair-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Configuration and security
│   │   ├── crud/         # Database operations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # RAG, indexing, extraction, storage
│   ├── requirements.txt
│   └── main.py
└── frontend/
    ├── src/
    └── package.json
```

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `backend/.env`, configure the database and optionally one or more LLM providers, then start the API:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Environment configuration

The repository does not require LLM credentials to be committed. API keys and security settings are read from environment variables.

See `.env.example` for the available configuration.

## Screenshots

Screenshots of the knowledge library, administration interface and RAG assistant can be added here for the portfolio presentation.

## Internship context

This project was developed as a two-month summer internship project at **Nouvelair (July-August 2026)**.

The objective was to explore how an internal knowledge platform and a RAG-based conversational interface could improve access to company information while keeping generated answers connected to identifiable source resources.

## Technical highlights

- End-to-end Angular + FastAPI application
- RAG pipeline implemented from document ingestion to cited answer generation
- Portable local retrieval/indexing implementation
- Hybrid passage ranking rather than LLM-only question answering
- Persisted conversations and source citations for traceability
- Role-based resource management
- Multiple LLM providers with graceful fallback

## Author

**Jaouhar Bziouech**  
Software Engineering student - ESPRIT  
M2 Data Science in Business - PST&B
