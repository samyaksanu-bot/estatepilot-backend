from fastapi import APIRouter
from app.projects.service import create_project, get_projects

router = APIRouter(prefix="/projects")

@router.post("/")
def create_new_project(payload: dict):
    project = create_project(payload)
    return {"status": "created", "project": project}

@router.get("/{tenant_id}")
def list_projects(tenant_id: str):
    return get_projects(tenant_id)
