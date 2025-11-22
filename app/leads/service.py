from app.database import supabase
from app.leads.models import Lead

def create_lead(data):
    lead = Lead(**data)
    supabase.table("leads").insert(lead.dict()).execute()
    return lead

def get_leads(tenant_id):
    response = supabase.table("leads").select("*").eq("tenant_id", tenant_id).execute()
    return response.data

def update_lead_score(lead_id, score):
    supabase.table("leads").update({"score": score}).eq("lead_id", lead_id).execute()
    return {"lead_id": lead_id, "score": score}
