from app.database import supabase
from app.projects.models import Project

def create_project(data):
    project = Project(**data)
    supabase.table("projects").insert(project.dict()).execute()
    return project

def get_projects(tenant_id):
    result = supabase.table("projects").select("*").eq("tenant_id", tenant_id).execute()
    return result.data
