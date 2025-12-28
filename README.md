# Silentbot AI [Enterprise Server]

**Status:** ONLINE  
**Version:** 3.1.0 (Enterprise)

Silentbot AI is a production-grade AI Chatbot platform built with Next.js 16, Vercel AI SDK, and Enterprise-grade observability. It supports multi-model routing (Google Gemini, xAI, OpenAI), resumable streams, and full session replay analytics.

## 🚀 Quick Start (Production)
http://silentbotai.com
http://silentbot.online 

# Silentbot-AI

## System Architecture

Silentbot-AI is organized as a multi-service platform that connects user-facing experiences to an AI orchestration layer and persistent data stores.

### Services

- **Web app (`apps/web`)**: React + Vite frontend that renders the user experience and calls the backend API.
- **Backend API (`apps/backend`)**: FastAPI service that handles orchestration, session management, tool routing, and exposes health endpoints.
- **Model gateway (planned)**: Provider connectors for LLMs, tool calling, and evaluation workflows.
- **Worker/queue (planned)**: Background processing for ingestion, indexing, and scheduled tasks.

### Data Stores

- **Primary database (planned)**: PostgreSQL for user data, conversations, and metadata.
- **Vector store (planned)**: pgvector or a managed vector database for embeddings and retrieval.
- **Object storage (planned)**: Blob store for documents, logs, and model artifacts.

### AI Pipeline

1. **Ingestion**: Capture user inputs and documents via the API.
2. **Indexing**: Generate embeddings and store them in the vector store.
3. **Retrieval**: Fetch relevant context for the user query.
4. **Generation**: Call the model gateway and assemble the response.
5. **Delivery**: Return results to the web app and persist conversation state.

## Components and Interaction

1. The **web app** calls the **backend API** for chat, ingestion, and retrieval endpoints.
2. The **backend API** persists metadata in the **primary database** and triggers **worker jobs**.
3. **Workers** create embeddings, store them in the **vector store**, and update the **primary database**.
4. The **backend API** queries the **vector store** and **model gateway** to produce responses.

## Repository Layout

```
apps/
  backend/   # FastAPI service (entry: app/main.py)
  web/       # React web app (entry: src/main.jsx)
```

## Getting Started

### Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
``
