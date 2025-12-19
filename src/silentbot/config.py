import os
from dotenv import load_dotenv

load_dotenv()

# --- PROJECT INFO ---
VERSION = "5.2.0-ULTIMATE"
PROJECT_NAME = "SilentBot AI"

# --- API KEYS (LOADED FROM ENV ONLY - NO HARDCODED SECRETS) ---
# Users must create a .env file based on .env.example
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- SETTINGS ---
DEFAULT_MODEL = os.getenv("SILENTBOT_MODEL", "gpt-4o") 
# If keys are missing, system will fallback to local/mock or error gracefully

# SECRETS - HIDDEN FROM SOURCE CODE
PRO_UNLOCK_CODE = os.getenv("PRO_UNLOCK_CODE", "CHANGE_ME_IN_ENV") 
ADMIN_LOG_CODE = os.getenv("ADMIN_LOG_CODE", "CHANGE_ME_IN_ENV")

NORMAL_MAX_TOKENS = 1024
PRO_MAX_TOKENS = 4096

# --- DIRECTORIES ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)