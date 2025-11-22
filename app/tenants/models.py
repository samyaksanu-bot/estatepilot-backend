from pydantic import BaseModel
from uuid import uuid4

class Tenant(BaseModel):
    tenant_id: str = str(uuid4())
    name: str
    contact_email: str
    status: str = "active"
