from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from ..config import settings

class TokenData(BaseModel):
    user_id: str
    organization_id: str
    email: str

class TokenPayload(BaseModel):
    user_id: str
    organization_id: str
    email: str
    iat: int
    exp: int

def create_access_token(user_id: str, organization_id: str, email: str) -> str:
    """Create JWT token with org_id"""
    now = datetime.utcnow()
    expire = now + timedelta(hours=settings.jwt_expiration_hours)
    
    payload = {
        "user_id": user_id,
        "organization_id": organization_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def verify_token(token: str) -> TokenPayload:
    """Verify JWT token and extract claims"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(token: str) -> TokenPayload:
    """Dependency to get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        return verify_token(token)
    except JWTError:
        raise credentials_exception