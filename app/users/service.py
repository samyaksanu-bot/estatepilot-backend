from app.database import supabase
from app.users.models import User
from app.core.security import hash_password, verify_password
from app.core.auth import create_jwt

def create_user(data):
    data["password_hash"] = hash_password(data["password"])
    del data["password"]
    user = User(**data)
    supabase.table("users").insert(user.dict()).execute()
    return user

def login_user(email, password):
    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        return None

    user_data = response.data[0]
    
    if not verify_password(password, user_data["password_hash"]):
        return None

    token = create_jwt({"user_id": user_data["user_id"], "tenant_id": user_data["tenant_id"]})

    return {"token": token, "user": user_data}
