# app/auth.py
import os
import jwt
from fastapi import Request, HTTPException, Header, Depends
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# Load secret from .env or fallback
SECRET_KEY = os.getenv("OPENAI_API_KEY", "fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 1. Create token for authenticated users
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 2. Decode and validate a JWT
def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 3. Dependency to decode JWT from Authorization header
def get_current_payload(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    return decode_jwt(token)

# 4. Extract fleet_id from token
def get_fleet_id(payload: Dict = Depends(get_current_payload)) -> int:
    fleet_id = payload.get("fleet_id")
    if fleet_id is None:
        raise HTTPException(status_code=403, detail="Missing fleet_id in token")
    return fleet_id

# 5. Dummy authentication (use DB in real scenario)
def authenticate_user(username: str, password: str) -> bool:
    return username == "admin" and password == "password123"


def get_current_payload(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    print("Auth header received:", auth_header)  # DEBUG
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    ...

