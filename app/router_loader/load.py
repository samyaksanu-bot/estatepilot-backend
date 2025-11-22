import importlib
import pkgutil
from fastapi import APIRouter
from pathlib import Path

def load_all_routers():
    router = APIRouter()

    app_path = Path(__file__).resolve().parent.parent

    for module_info in pkgutil.walk_packages([str(app_path)]):
        module_name = module_info.name

        # Only load modules ending with .routes
        if module_name.endswith(".routes"):
            full_module = f"app.{module_name}"
            try:
                module = importlib.import_module(full_module)
                if hasattr(module, "router"):
                    router.include_router(getattr(module, "router"))
            except Exception as e:
                print(f"Router load error in {full_module}: {e}")

    return router
