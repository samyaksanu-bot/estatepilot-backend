from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

class Lead(BaseModel):
    lead_id: str = str(uuid4())
    tenant_id: str
    project_id: str
    name: str
    phone: str
    source: str = "unknown"
    created_at: str = datetime.utcnow().isoformat()
    score: int = 0
    status: str = "new"
