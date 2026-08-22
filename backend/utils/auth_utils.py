from datetime import datetime, timedelta
from typing import Any, Union, Optional
import jwt
from config.settings import settings
import hashlib
import secrets
import string

# Password hashing
def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    
    TODO: In production, use bcrypt or argon2
    pip install bcrypt
    
    Example:
        from bcrypt import hashpw, gensalt, checkpw
        hashed = hashpw(password.encode(), gensalt())
    """
    salt = secrets.token_hex(32)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hashed = password_hash.split("$")
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        decoded_token = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return decoded_token
    except jwt.PyJWTError:
        return None


def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"user_{secrets.token_hex(16)}"


def generate_conversation_id() -> str:
    """Generate unique conversation ID"""
    return f"conv_{secrets.token_hex(16)}"


def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg_{secrets.token_hex(16)}"
