import os
from pathlib import Path

# Identity
PRODUCT_NAME = "Silent Bot"
OWNER = "@Silentbotoffical"
ENGINE_VERSION = "SilentLogic v3.0"

# Editions
EDITION_NORMAL = "Silent Bot CLI v2.5"
EDITION_PRO = "Silent Bot PRO Terminal v3.0"

# Security
UPDATE_KEY = "SILENT.123"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure dirs exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)