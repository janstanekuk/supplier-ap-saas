from supabase import create_client
from ..config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_anon_key
)

def get_supabase_admin():
    """Get Supabase admin client with service role key"""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )

def verify_supabase_token(token: str) -> dict:
    """Verify Supabase JWT token"""
    try:
        admin = get_supabase_admin()
        user = admin.auth.get_user(token)
        return user
    except Exception as e:
        return None