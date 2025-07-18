"""Database module for warehouse exchange system"""

from .supabase_client import SupabaseClient, get_client

__all__ = ["SupabaseClient", "get_client"]
