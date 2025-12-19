import sqlite3
import json
import os
import sys

# Add src to path to import config
sys.path.append(os.path.join(os.getcwd(), "src"))
from silentbot.config import DATA_DIR

DB_NAME = "silentbot_ultimate_v1.db"
DB_PATH = os.path.join(DATA_DIR, DB_NAME)
JSON_PATH = os.path.join("src", "silentbot", "core", "knowledge.json")

def merge():
    # Ensure dir exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize DB if missing
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, category TEXT, description TEXT, expert_prompt TEXT)""")
    
    if not os.path.exists(JSON_PATH):
        print(f"JSON not found at {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Merging {len(data)} knowledge entries into {DB_PATH}...")
    
    count = 0
    for item in data:
        try:
            c.execute("""
                INSERT OR REPLACE INTO knowledge (key, category, description, expert_prompt)
                VALUES (?, ?, ?, ?)
            """, (item["key"], item["category"], item["description"], item["expert_prompt"]))
            count += 1
        except Exception as e:
            print(f"Error merging {item['key']}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Success! Merged {count} entries.")

if __name__ == "__main__":
    merge()