# Contributing to SilentBot AI

Welcome to the development hub for SilentBot AI. We are building the future of Autonomous Agentic Intelligence (v2027).

## 🛠 Setup & Building

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Silentbotbd/Silentbot-AI.git
    cd Silentbot-AI
    ```

2.  **Environment**
    Ensure Python 3.11+ is installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Database**
    The system uses SQLite. It auto-initializes on first run.
    Admin Account is seeded automatically in `src/silentbot/core/db.py`.

## 🧪 Testing

Run the test suite (if available) or use the CLI in headless mode:
```bash
python main.py --cli --test
```

## 👨‍💻 Coding Conventions

*   **Style:** Follow PEP 8.
*   **Architecture:** Use the `src/silentbot` modular structure.
    *   `api/`: FastAPI Routers.
    *   `core/`: Business Logic (Agent, DB, Security).
    *   `ui/`: Frontend Assets.
*   **Security:** Never commit API keys. Use `.env`.

## 🚀 Pull Requests

1.  Fork the repo.
2.  Create a feature branch (`git checkout -b feature/amazing-ai`).
3.  Commit changes.
4.  Push and open a PR.

## 🤝 Community

Join the discussion on GitHub Issues for feature requests like "Custom Slash Commands" or "OpenTelemetry" support.
