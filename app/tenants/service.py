from app.database import supabase
from app.tenants.models import Tenant

def create_tenant(data):
    tenant = Tenant(**data)
    supabase.table("tenants").insert(tenant.dict()).execute()
    return tenant
