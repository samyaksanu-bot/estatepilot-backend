import json
import os
from functools import lru_cache

CLIENT_CONFIG_DIR = "app/client_configs"


@lru_cache
def load_client_config(client_id: str):
    """
    Loads client JSON config based on client_id.
    Example client_id: ojas_builders
    """

    filename = f"{client_id}.json"
    filepath = os.path.join(CLIENT_CONFIG_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Client config not found: {filename}")

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
