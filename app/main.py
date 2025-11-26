from fastapi import FastAPI
from app.router_loader.load import load_all_routers

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

# Load all routers automatically
app.include_router(load_all_routers())

@app.get("/health")
def health():
    return {"status": "OK"}
