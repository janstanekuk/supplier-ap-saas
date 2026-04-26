from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    organization_name: str
    full_name: Optional[str] = None

class SignupResponse(BaseModel):
    user_id: str
    organization_id: str
    email: str
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    user_id: str
    organization_id: str
    email: str
    access_token: str
    token_type: str = "bearer"

class CurrentUserResponse(BaseModel):
    user_id: str
    organization_id: str
    email: str
    role: str