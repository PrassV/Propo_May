from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.settings import settings
from app.db.session import get_db
from app.db.supabase import supabase
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.schemas.token import TokenPayload
from app.models.user import UserRole
from typing import Optional, List, Dict, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get the current user based on the JWT token.
    The token should be from Supabase auth.
    """
    # Use the token from either the header or the dependency
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        
    try:
        # Verify token with Supabase
        session = supabase.auth.get_session()
        if not session or not session.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )
            
        # Get user from our Supabase database
        user_repo = UserRepositorySupabase()
        user = await user_repo.get_by_supabase_uid(session.user.id)
        
        if not user:
            # If the user is in Supabase Auth but not our DB, create a minimal record
            user_data = {
                "email": session.user.email,
                "supabase_uid": session.user.id,
                "first_name": "",
                "last_name": "",
                "role": "tenant",  # Default role
                "status": "active"
            }
            user = await user_repo.create(user_data)
        
        return user
        
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )

async def get_current_active_user(current_user = Depends(get_current_user)):
    if current_user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user

def check_role(allowed_roles: List[str]):
    async def _check_role(current_user = Depends(get_current_active_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permissions",
            )
        return current_user
    return _check_role

# Role-specific dependencies
get_current_admin = check_role(["admin"])
get_current_owner = check_role(["owner", "admin"])
get_current_maintenance = check_role(["maintenance", "admin"]) 