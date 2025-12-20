# Silentbot AI [Enterprise Server]

**Status:** ONLINE  
**Version:** 3.1.0 (Enterprise)

Silentbot AI is a production-grade AI Chatbot platform built with Next.js 16, Vercel AI SDK, and Enterprise-grade observability. It supports multi-model routing (Google Gemini, xAI, OpenAI), resumable streams, and full session replay analytics.

## 🚀 Quick Start (Production)

### Option A: Docker (Recommended)
You can deploy Silentbot AI anywhere Docker is supported.

1.  **Build the image:**
    ```bash
    docker build -t silentbot-ai .
    ```
2.  **Run the container:**
    ```bash
    docker run -d -p 3000:3000 --env-file .env silentbot-ai
    ```

### Option B: Vercel (Managed)
1.  Import this repository to Vercel.
2.  Add the required Environment Variables.
3.  Deploy.

## 🛠️ Development Setup

1.  **Install dependencies:**
    ```bash
    pnpm install
    ```
2.  **Setup Database:**
    Ensure you have a Postgres database running, then:
    ```bash
    pnpm db:migrate
    ```
3.  **Run Development Server:**
    ```bash
    pnpm dev
    ```
    Access the Enterprise Dashboard at `http://localhost:3000`.

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in the following:

| Variable | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google AI Studio API Key. |
| `POSTGRES_URL` | PostgreSQL connection string. |
| `REDIS_URL` | Redis connection string. |
| `AUTH_SECRET` | Random string for session encryption. |
| `NEXT_PUBLIC_STATSIG_CLIENT_KEY` | Statsig Client Key for analytics. |

## 🏗️ Architecture

*   **Frontend:** Next.js 16 (App Router), TailwindCSS, Shadcn/UI
*   **AI Engine:** Vercel AI SDK (Streaming, Tools, Generative UI)
*   **Database:** PostgreSQL (via Drizzle ORM) + Redis (Session Store)
*   **Analytics:** Statsig (Feature Flags & Session Replay) + Vercel Analytics
*   **Observability:** OpenTelemetry (OTel)

## 📄 License
Private Enterprise License.