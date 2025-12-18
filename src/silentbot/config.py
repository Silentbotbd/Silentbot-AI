import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- PROJECT INFO ---
VERSION = "5.5.0-PROD"
PROJECT_NAME = "SilentBot AI"

# --- API KEYS (Loaded from .env) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HOSTION_API_KEY = os.getenv("HOSTION_API_KEY", "")

# --- SETTINGS ---
DEFAULT_MODEL = os.getenv("SILENTBOT_MODEL", "gpt-4o")
PRO_UNLOCK_CODE = os.getenv("PRO_UNLOCK_CODE", "MYSECRETPROCODE")
ADMIN_LOG_CODE = os.getenv("ADMIN_LOG_CODE", "MRSILENT.ADMIN.LOG.VIEW.2025")

NORMAL_MAX_TOKENS = 512
PRO_MAX_TOKENS = 4096 # Increased for 2027 Pro

# --- DIRECTORIES ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
