import sys
import argparse
import uvicorn
from src.silentbot.api.main import app
from src.silentbot.cli.main import run_cli
from src.silentbot.config import PROJECT_NAME, VERSION

def main():
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} v{VERSION}")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API mode (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for API mode (default: 0.0.0.0)")
    
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        print(f"Starting {PROJECT_NAME} API on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
