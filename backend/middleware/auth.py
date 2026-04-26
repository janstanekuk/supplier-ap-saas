from fastapi import Request, HTTPException, status
from ..services.auth import get_current_user

async def verify_org_access(request: Request):
    """
    Middleware to verify user has access to organization.
    Extracts org_id from JWT and makes it available to routes.
    """
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        token_data = get_current_user(token)
        request.state.user_id = token_data.user_id
        request.state.organization_id = token_data.organization_id
        request.state.email = token_data.email
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )