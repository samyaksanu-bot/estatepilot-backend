import json
from pathlib import Path

BASE_DIR = Path(__file__).parent

def load_client_config(client_id: str):
    file_path = BASE_DIR / f"{client_id}.json"
    if not file_path.exists():
        raise ValueError("Client config not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
