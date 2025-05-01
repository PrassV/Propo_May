from typing import Callable, Optional
from fastapi import Depends
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.repositories.property_repository_supabase import PropertyRepositorySupabase
from app.db.repositories.unit_repository_supabase import UnitRepositorySupabase

# Factory for getting repository instances without needing a DB session
def get_repository(repo_class: Callable):
    """
    Factory function to get a repository instance.
    All repositories are now Supabase-based and don't need a db session.
    """
    
    async def _get_repo():
        return repo_class()
    
    return _get_repo

# Create specific dependencies for each repository
get_user_repository = get_repository(UserRepositorySupabase)
get_property_repository = get_repository(PropertyRepositorySupabase)
get_unit_repository = get_repository(UnitRepositorySupabase) 