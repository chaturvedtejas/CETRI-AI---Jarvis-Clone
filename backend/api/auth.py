from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.models import User, Session as DBSession, get_db
from utils.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    generate_user_id
)
from datetime import timedelta

router = APIRouter()


class UserLogin(BaseModel):
    email: str
    password: str


class UserSignup(BaseModel):
    email: str
    password: str
    name: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/signup", response_model=TokenResponse)
async def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Args:
        user_data: Email, password, name
        db: Database session
    """
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = generate_user_id()
    password_hash = hash_password(user_data.password)
    
    new_user = User(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    token = create_access_token(subject=new_user.id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "created_at": new_user.created_at.isoformat()
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user
    
    Args:
        user_data: Email and password
        db: Database session
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    token = create_access_token(subject=user.id)
    
    # Save session to database
    session = DBSession(
        id=f"session_{token[:20]}",
        user_id=user.id,
        token=token,
        expires_at=user.created_at + timedelta(days=7)
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    
    Args:
        token: JWT token
        db: Database session
    """
    
    # TODO: Extract token from header
    # For now, this is a placeholder
    
    user = db.query(User).first()  # Placeholder
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user


@router.post("/logout")
async def logout(
    token: str,
    db: Session = Depends(get_db)
):
    """Logout user by invalidating token"""
    
    session = db.query(DBSession).filter(DBSession.token == token).first()
    if session:
        session.is_valid = False
        db.commit()
    
    return {"message": "Logged out successfully"}
