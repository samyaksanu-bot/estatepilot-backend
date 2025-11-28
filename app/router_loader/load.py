from fastapi import APIRouter
import importlib
import pkgutil
import app

def load_all_routers() -> APIRouter:
    router = APIRouter()

    for module in pkgutil.iter_modules(app.__path__):
        module_name = module.name

        try:
            routes_module = importlib.import_module(
                f"app.{module_name}.routes"
            )
            router.include_router(routes_module.router)
        except ModuleNotFoundError:
            continue

    return router
