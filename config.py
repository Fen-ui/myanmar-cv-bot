import json, os

with open("config.json", encoding="utf-8") as f:
    _j = json.load(f)

BOT_TOKEN        = _j["bot_token"]
OPENROUTER_KEY   = _j["openrouter_key"]
DB_PATH          = _j.get("db_path",          "cvbot.db")
OUTPUT_DIR       = _j.get("output_dir",        "cv_output")
DEFAULT_TEMPLATE = _j.get("default_template",  "modern")
FREE_LIMIT       = int(_j.get("free_limit_per_user", 3))

os.makedirs(OUTPUT_DIR, exist_ok=True)
