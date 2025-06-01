from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from app.auth import authenticate_user, create_access_token, get_fleet_id
from app.llm import process_query

router = APIRouter()

# ---------------------
# Healthcheck Endpoint
# ---------------------
@router.get("/ping")
def healthcheck():
    return {"status": "ok"}

# ---------------------
# Chat Endpoint (JWT protected)
# ---------------------
@router.post("/chat")
async def chat(request: Request, fleet_id: int = Depends(get_fleet_id)):
    body = await request.json()
    query = body.get("query", "")
    response = await process_query(query, fleet_id)
    return {"answer": response}

# ---------------------
# Login Endpoint (Issues JWT)
# ---------------------
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    if not authenticate_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Customize claims as needed
    token = create_access_token({
        "sub": data.username,
        "fleet_id": 1  # This should come from DB in real app
    })

    return {"access_token": token, "token_type": "bearer"}

