from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from typing import Dict, Any, Optional
import logging
from app.core.config.settings import settings
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.supabase import supabase
from app.models.user import UserRole

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validate the token and get the current user from Supabase.
    
    This verifies the JWT with Supabase and retrieves the user's data.
    """
    try:
        # Set the session token to the provided token
        supabase.auth.set_session(token)
        
        # Get the session user
        session = supabase.auth.get_session()
        
        if not session or not session.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get the user from our database table using the Supabase user ID
        user_repo = UserRepositorySupabase()
        user = await user_repo.get_by_id(session.user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found in database",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Check if the current user is active.
    """
    if current_user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def check_role(allowed_roles: list[str]):
    """
    Check if the user has one of the allowed roles.
    """
    async def _check_role(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return _check_role

# Role-specific dependencies
get_current_admin = check_role(["admin"])
get_current_owner = check_role(["owner", "admin"])
get_current_tenant = check_role(["tenant", "owner", "admin"])
get_current_maintenance = check_role(["maintenance", "admin"]) 