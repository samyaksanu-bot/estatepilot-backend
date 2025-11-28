from fastapi import FastAPI
from app.router_loader.load import load_all_routers

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

# ✅ Auto load ALL routers (including WhatsApp)
app.include_router(load_all_routers())

@app.get("/health")
def health():
    return {"status": "ok"}
