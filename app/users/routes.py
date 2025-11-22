from fastapi import APIRouter
from app.users.service import create_user, login_user

router = APIRouter(prefix="/users")

@router.post("/signup")
def signup_user(payload: dict):
    user = create_user(payload)
    return {"status": "created", "user": user}

@router.post("/login")
def login(payload: dict):
    result = login_user(payload["email"], payload["password"])
    if not result:
        return {"status": "failed", "message": "Invalid credentials"}
    return {"status": "success", "auth": result}
