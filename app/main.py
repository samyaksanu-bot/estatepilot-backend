from fastapi import FastAPI
from app.whatsapp.routes import router as whatsapp_router

app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)

app.include_router(whatsapp_router)

@app.get("/health")
def health():
    return {"status": "ok"}
