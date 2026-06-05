from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils.auth_utils import create_access_token

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserSignup(BaseModel):
    email: str
    password: str
    name: str

# Mock Database for demo
USERS = {}

@router.post("/signup")
async def signup(user: UserSignup):
    if user.email in USERS:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    USERS[user.email] = {
        "email": user.email,
        "name": user.name,
        "password": user.password # IN PRODUCTION: Hash this password!
    }
    
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": user.email, "name": user.name}}

@router.post("/login")
async def login(user: UserLogin):
    if user.email not in USERS or USERS[user.email]["password"] != user.password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer", "user": {"email": user.email, "name": USERS[user.email]["name"]}}
