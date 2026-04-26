from pydantic import BaseModel
from typing import Optional

class SignupRequest(BaseModel):
    email: str
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
    email: str
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