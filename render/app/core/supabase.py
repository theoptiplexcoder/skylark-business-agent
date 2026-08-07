from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()


def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_admin_client() -> Client:
    if settings.SUPABASE_SERVICE_KEY:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return get_supabase_client()


supabase: Client = get_supabase_client()
supabase_admin: Client = get_supabase_admin_client()
