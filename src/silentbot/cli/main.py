import os
import uuid
import time
import random
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from ..config import PROJECT_NAME, VERSION, PRO_UNLOCK_CODE
from ..core.agent import Agent
from ..core.db import db

THEMES = [{"border":"green"},{"border":"magenta"},{"border":"blue"},{"border":"yellow"}]
console = Console()

def get_cli_user_id():
    config_path = "cli_user.id"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return f.read().strip()
    uid = str(uuid.uuid4())
    with open(config_path, "w") as f:
        f.write(uid)
    return uid

def run_cli():
    parser = argparse.ArgumentParser(description="SilentBot CLI")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    parser.add_argument("--prompt", type=str, help="Initial prompt")
    args = parser.parse_known_args()[0]

    uid = get_cli_user_id()
    user = db.ensure_user(uid) if hasattr(db, 'ensure_user') else db.create_user(f"cli_{uid[:8]}", "clipass", role="cli")
    # Refresh
    user = db.get_user_by_id(uid) or user
    is_pro = user["is_pro"]

    if args.headless and args.prompt:
        # One-shot mode
        agent = Agent(mode="pro" if is_pro else "normal", user_id=uid)
        res = agent.run(args.prompt, [])
        print(res["response"])
        return

    theme = random.choice(THEMES)
    console.print(Panel(f"{PROJECT_NAME} v{VERSION} [PRO: {is_pro}]", border_style=theme["border"]))
    console.print("[dim]Commands: /memory <fact>, /unlock <code>, /config, /exit[/dim]")

    current_sid = None

    while True:
        msg = Prompt.ask("You").strip()
        if not msg: continue
        
        # Slash Commands
        if msg.startswith("/exit"): break
        if msg.startswith("/unlock"):
            code = msg.replace("/unlock", "").strip()
            if code == PRO_UNLOCK_CODE:
                db.make_user_pro(uid)
                is_pro = True
                console.print("[green]Pro Unlocked![/green]")
            else:
                console.print("[red]Invalid[/red]")
            continue
        if msg.startswith("/memory"):
            fact = msg.replace("/memory", "").strip()
            db.add_memory(uid, fact)
            console.print("[cyan]Memory Saved.[/cyan]")
            continue
        if msg.startswith("/config"):
            console.print(f"User: {uid}\nPro: {is_pro}\nReqs: {user.get('req_count',0)}")
            console.print("\n[bold]ACTIVE POLICIES:[/bold]\n1. ALLOW: read, glob, search, list\n2. ASK_USER: write, replace, shell")
            continue

        if not current_sid:
            current_sid = db.create_session(uid, "CLI")

        # Chat
        agent = Agent(mode="pro" if is_pro else "normal", user_id=uid)
        
        # Check Limits
        if not is_pro and user["req_count"] >= 30:
            console.print("[red]Limit Reached (30). /unlock to continue.[/red]")
            continue
            
        with console.status("Thinking..."):
            res = agent.run(msg, db.get_history(current_sid))
            db.add_message(current_sid, "user", msg)
            db.add_message(current_sid, "assistant", res["response"])
            db.increment_request_count(uid)
            
        console.print(Panel(Markdown(res["response"])), border_style=theme["border"])

if __name__ == "__main__":
    run_cli()