from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from ..database import get_db
from ..models import User, Organization, UserRole
from ..schemas.auth import SignupRequest, SignupResponse, LoginRequest, LoginResponse, CurrentUserResponse
from ..services.auth import create_access_token, get_current_user, TokenPayload
from ..services.supabase import get_supabase_admin
from ..config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Create new user and organization"""
    try:
        from ..services.supabase import supabase
        
        # Create user in Supabase Auth (regular sign up)
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise Exception("Failed to create user in Supabase")
        
        supabase_id = auth_response.user.id
        
        # Create organization
        org_id = uuid.uuid4()
        slug = request.organization_name.lower().replace(" ", "-")
        
        organization = Organization(
            id=org_id,
            name=request.organization_name,
            slug=slug,
            plan="free"
        )
        db.add(organization)
        
        # Create user in database
        user = User(
            id=uuid.uuid4(),
            supabase_id=supabase_id,
            organization_id=org_id,
            email=request.email,
            role=UserRole.admin
        )
        db.add(user)
        await db.commit()
        
        # Create access token
        access_token = create_access_token(
            user_id=str(user.id),
            organization_id=str(org_id),
            email=request.email
        )
        
        return SignupResponse(
            user_id=str(user.id),
            organization_id=str(org_id),
            email=request.email,
            access_token=access_token
        )
        
    except Exception as e:
        await db.rollback()
        print(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}"
        )

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and return JWT token"""
    try:
        from ..services.supabase import supabase
        
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise Exception("Invalid credentials")
        
        # Find user in database
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create access token
        access_token = create_access_token(
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            email=user.email
        )
        
        return LoginResponse(
            user_id=str(user.id),
            organization_id=str(user.organization_id),
            email=user.email,
            access_token=access_token
        )
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    authorization: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get current user from token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token"
        )
    
    token = authorization.replace("Bearer ", "")
    token_data = get_current_user(token)
    
    return CurrentUserResponse(
        user_id=token_data.user_id,
        organization_id=token_data.organization_id,
        email=token_data.email,
        role="member"  # Will update from database in Week 3
    )