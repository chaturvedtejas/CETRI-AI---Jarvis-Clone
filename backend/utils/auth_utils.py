from datetime import datetime, timedelta
from typing import Any, Union
import jwt
from config.settings import settings

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return decoded_token
    except jwt.PyJWTError:
        return None
