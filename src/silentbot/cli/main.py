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

# Expanded Themes for "Smart and Smooth" variety
THEMES = [
    {"border": "green", "title_color": "green"},
    {"border": "magenta", "title_color": "magenta"},
    {"border": "blue", "title_color": "blue"},
    {"border": "yellow", "title_color": "yellow"},
    {"border": "cyan", "title_color": "cyan"},
    {"border": "bright_red", "title_color": "bright_red"},
    {"border": "bright_white", "title_color": "bright_white"},
    {"border": "orange1", "title_color": "orange1"},
    {"border": "deep_pink2", "title_color": "deep_pink2"},
]

BANNER_ART = r"""
  ███████╗██╗██╗     ███████╗███╗   ██╗████████╗
  ██╔════╝██║██║     ██╔════╝████╗  ██║╚══██╔══╝
  ███████╗██║██║     █████╗  ██╔██╗ ██║   ██║
  ╚════██║██║██║     ██╔══╝  ██║╚██╗██║   ██║
  ███████║██║███████╗███████╗██║ ╚████║   ██║
  ╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝
              SILENT BOT AI/CLI
"""

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
    
    # Ensure user exists in DB
    user = db.get_user_by_id(uid)
    if not user:
        user = db.create_user(uid, username=f"cli_{{uid[:8]}}", role="cli")

    is_pro = user["is_pro"]

    if args.headless and args.prompt:
        # One-shot mode
        agent = Agent(mode="pro" if is_pro else "normal", user_id=uid)
        res = agent.run(args.prompt, [])
        print(res["response"])
        return

    # Randomly select a theme for this session
    theme = random.choice(THEMES)
    border_color = theme["border"]
    title_color = theme["title_color"]

    # Display Banner with the chosen theme
    console.print(Panel(
        f"[{{title_color}}]{BANNER_ART}[/{{title_color}}][bold {{title_color}}]{PROJECT_NAME} v{VERSION}[/bold {{title_color}}] [PRO: {'ON' if is_pro else 'OFF'}]", 
        border_style=border_color
    ))
    console.print("[dim]Commands: /memory <fact>, /unlock <code>, /clear, /config, /exit[/dim]")

    current_sid = db.create_session(uid, "CLI Session")

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
                console.print("[red]Invalid Code[/red]")
            continue
            
        if msg.startswith("/memory"):
            fact = msg.replace("/memory", "").strip()
            if fact:
                db.add_memory(uid, fact)
                console.print("[cyan]Memory Saved.[/cyan]")
            continue
            
        if msg.startswith("/clear"):
            console.clear()
            # Re-pick theme on clear for "dynamic" feel
            theme = random.choice(THEMES)
            border_color = theme["border"]
            title_color = theme["title_color"]
            console.print(Panel(
                f"[{{title_color}}]{BANNER_ART}[/{{title_color}}][bold {{title_color}}]{PROJECT_NAME} v{VERSION}[/bold {{title_color}}]", 
                border_style=border_color
            ))
            current_sid = db.create_session(uid, "CLI Session (Cleared)")
            continue
            
        if msg.startswith("/config"):
            console.print(f"User ID: {uid}")
            console.print(f"Pro Mode: {is_pro}")
            console.print(f"Requests: {user.get('req_count', 0)}")
            continue

        # Chat Logic
        agent = Agent(mode="pro" if is_pro else "normal", user_id=uid)
        
        # Check Limits
        if not is_pro and user["req_count"] >= 30:
            console.print("[red]Free limit reached (30 requests). Use /unlock to upgrade.[/red]")
            continue
            
        # Display thinking status
        with console.status("Thinking...", spinner="dots"):
            try:
                # Get history for context
                history = db.get_history(current_sid)
                
                # Add user message to DB first
                db.add_message(current_sid, "user", msg)
                
                # Run Agent
                res = agent.run(msg, history)
                
                # Save assistant response
                db.add_message(current_sid, "assistant", res["response"])
                db.increment_request_count(uid)
                
                # Display output
                console.print(Panel(Markdown(res["response"]), title="SilentBot", border_style=border_color))
                
                # Show citations/steps if available (Advanced Feature)
                if "steps" in res and res["steps"]:
                    for step in res["steps"]:
                        if "TOOL" in step.get("content", ""):
                             console.print(f"[dim]{step['content']}[/dim]")

            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    run_cli()