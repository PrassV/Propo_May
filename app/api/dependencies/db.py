from typing import Callable, Optional
from fastapi import Depends
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.repositories.property_repository import PropertyRepository
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# Factory for getting repository instances
# This helps with dependency injection and makes switching between
# SQLAlchemy and Supabase implementations easier

def get_repository(repo_class: Callable):
    """
    Factory function to get a repository instance.
    This works with both SQLAlchemy-based repositories that need a db session
    and Supabase-based repositories that don't.
    """
    
    async def _get_repo(db: Optional[AsyncSession] = Depends(get_db)):
        if 'Supabase' in repo_class.__name__:
            # Supabase repositories don't need a db session
            return repo_class()
        else:
            # SQLAlchemy repositories need a db session
            return repo_class(db)
    
    return _get_repo

# Create specific dependencies for each repository
get_user_repository = get_repository(UserRepositorySupabase) 