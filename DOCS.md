# SilentBot AI - User Manual (v5.5)

## 🚀 Getting Started

SilentBot is an advanced AI Agent capable of coding, writing, and system automation.

### Installation
1.  **Clone:** `git clone https://github.com/Silentbotbd/Silentbot-AI`
2.  **Install:** `pip install -r requirements.txt`
3.  **Run:** `python main.py`

### System Requirements
*   Python 3.11+
*   Windows/Linux/macOS
*   4GB RAM recommended

---

## 💻 CLI Usage

The CLI is the power-user interface.
Run: `python main.py --cli`

### Slash Commands
*   `/exit`: Quit the CLI.
*   `/unlock <code_key>`: Activate Pro Mode.
*   `/memory <text>`: Save a fact to long-term memory (e.g., `/memory My api key is 123`).
*   `/config`: View current user status and usage.

### Headless Mode (Automation)
Run single commands without opening the interactive shell:
```bash
python main.py --cli --headless --prompt "Write a Python script to scan ports"
```

---

## 🧠 Capabilities (Knowledge Base)

SilentBot has been pre-trained (via database seeding) on:
*   **Web:** JS, TS, HTML, CSS, PHP
*   **Systems:** Python, Java, C++, Go, Rust
*   **Data:** SQL, R, Swift, Kotlin
*   **Scripting:** Bash, PowerShell, Lua
*   **Writing:** Essays, Technical Docs, Resumes, Cover Letters

### Agentic Memory
SilentBot uses a ReAct loop. It can:
1.  **Search Knowledge:** Retrieve expert prompts.
2.  **Recall Memory:** Remember facts you saved via `/memory`.
3.  **Use Tools:** Calculate math, check system time.

---

## 🔐 Authentication & Pro Mode

*   **Guest:** Limited to 30 messages. No coding allowed.
*   **Pro:** Unlimited messages. Full coding support.
*   **Admin:** Full system access.

**Admin Login:** `Silentbotbd` / `SilentBotBd2025 @@>!?`

---

## 📦 Build for Distribution

To create a standalone `.exe` for users:
1.  Run `python build_executable.py`
2.  Find the file in `dist/SilentBot.exe`
3.  Share this file. Users do not need Python installed.

---

## 🤝 Contributing

See `CONTRIBUTING.md` for dev setup.
