import os, uuid, time, random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from ..config import PROJECT_NAME, VERSION, PRO_UNLOCK_CODE
from ..core.ai import call_ai
from ..core.db import db

THEMES = [{"border":"green"},{"border":"magenta"},{"border":"blue"},{"border":"yellow"}]
console = Console()

def run_cli():
    uid = str(uuid.uuid4())
    user = db.ensure_user(uid)
    theme = random.choice(THEMES)
    console.print(Panel(f"{PROJECT_NAME} v{VERSION}", border_style=theme["border"]))
    while True:
        msg = Prompt.ask("You").strip()
        if msg.lower() == "exit": break
        res = call_ai([{"role":"user", "content":msg}])
        console.print(Panel(Markdown(res["content"]), border_style=theme["border"]))

if __name__ == "__main__":
    run_cli()
