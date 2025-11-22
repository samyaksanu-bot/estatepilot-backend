from pydantic import BaseModel
from uuid import uuid4

class User(BaseModel):
    user_id: str = str(uuid4())
    tenant_id: str
    email: str
    password_hash: str
    role: str = "admin"
