from fastapi import APIRouter
from app.tenants.service import create_tenant

router = APIRouter(prefix="/tenants")

@router.post("/")
def register_tenant(payload: dict):
    tenant = create_tenant(payload)
    return {"status": "created", "tenant": tenant}
