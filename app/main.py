from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

# Core boot logic
from app.app.brain_loader import load_brain
from app.app.context import COUNTERS, SCORING

# Routers
from app.app.whatsapp.routes import router as whatsapp_router
from app.leads.routes import router as leads_router
from app.users.routes import router as users_router
from app.tenants.routes import router as tenants_router
from app.projects.routes import router as projects_router
from app.scoring.routes import router as scoring_router


# --------------------------------------------------
# LOAD BRAIN ON STARTUP
# --------------------------------------------------
loaded_counters, loaded_scoring = load_brain()
COUNTERS.update(loaded_counters)
SCORING.update(loaded_scoring)

print("✅ Brain loaded:", list(COUNTERS.keys()))
print("✅ EstatePilot backend booting")


# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------
app = FastAPI(
    title="EstatePilot Backend",
    version="1.0.0"
)


# --------------------------------------------------
# REGISTER ROUTERS — THESE ARE SAFE
# --------------------------------------------------
app.include_router(whatsapp_router)
app.include_router(leads_router)
app.include_router(users_router)
app.include_router(tenants_router)
app.include_router(projects_router)
app.include_router(scoring_router)




# --------------------------------------------------
# HEALTH CHECK (RENDER USES THIS)
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

    return {"status": "ok"}
