from pydantic import BaseModel
from uuid import uuid4

class Project(BaseModel):
    project_id: str = str(uuid4())
    tenant_id: str
    name: str
    location: str
    price_start: float
    brochure_url: str = None
    status: str = "active"
