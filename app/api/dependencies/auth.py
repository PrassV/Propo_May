from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from typing import Dict, Any, Optional, List
import logging
from app.core.config.settings import settings
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.supabase import supabase
from app.models.user import UserRole
from app.core.errors.error_handler import handle_permission_error

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

# Create a request-scoped variable for the active role
active_role_key = "active_user_role"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validate the token and get the current user from Supabase.
    
    This verifies the JWT with Supabase and retrieves the user's data.
    """
    try:
        # Create a new client with the token
        client = supabase.auth.get_user(token)
        
        if not client or not client.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get the user from our database table using the Supabase user ID
        user_repo = UserRepositorySupabase()
        user = await user_repo.get_by_id(client.user.id)
        
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

async def get_current_active_user(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if the current user is active and set active role.
    """
    if current_user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Store the user's current role in request state
    # This allows role switching within a session
    if active_role_key not in request.state.__dict__:
        request.state.__dict__[active_role_key] = current_user.get("role")
    
    return current_user

async def get_user_available_roles(user_id: str) -> List[str]:
    """
    Get the list of roles available to the user from user_roles table.
    """
    try:
        # Query the user_roles table in Supabase
        resp = supabase.table("user_roles").select("role").eq("user_id", user_id).execute()
        data = resp.data or []
        # Extract roles as list of strings
        return [r.get("role") for r in data if r.get("role")]
    except Exception as e:
        logger.error(f"Error fetching roles for user {user_id}: {e}")
        return []

def get_active_role(request: Request) -> str:
    """Get the active role from request state"""
    return request.state.__dict__.get(active_role_key, "tenant")

def check_role(allowed_roles: list[str]):
    """
    Check if the user has one of the allowed roles.
    This uses the active role from request state.
    """
    async def _check_role(
        request: Request,
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        # Get active role from request state
        active_role = get_active_role(request)
        
        if active_role not in allowed_roles:
            # Get available roles to provide better error messages
            available_roles = await get_user_available_roles(current_user.get("user_id"))
            
            # Check if the user has any of the allowed roles available
            has_any_allowed_role = any(role in allowed_roles for role in available_roles)
            
            if has_any_allowed_role:
                # User has the role but it's not active - suggest switching
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires {', '.join(allowed_roles)} role. Please switch to that role first."
                )
            else:
                # User doesn't have any of the required roles
                handle_permission_error(
                    entity="resource", 
                    operation="access",
                    user_role=active_role
                )
                
        return current_user
    return _check_role

async def switch_role(
    request: Request,
    new_role: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> bool:
    """
    Switch the user's active role.
    
    Args:
        request: The FastAPI request object
        new_role: The role to switch to
        current_user: The current user
        
    Returns:
        bool: True if successful
        
    Raises:
        HTTPException: If the role switch is not allowed
    """
    available_roles = await get_user_available_roles(current_user.get("user_id"))
    
    if new_role not in available_roles:
        handle_permission_error(
            entity="role", operation="switch", user_role=current_user.get("role")
        )
    
    # Log the role switch audit
    from datetime import datetime
    try:
        supabase.table("role_switch_audit").insert({
            "user_id": current_user.get("user_id"),
            "from_role": get_active_role(request),
            "to_role": new_role,
            "switched_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as audit_err:
        logger.warning(f"Role switch audit failed: {audit_err}")
    # Update the active role in request state
    request.state.__dict__[active_role_key] = new_role
    return True

# Role-specific dependencies
get_current_admin = check_role(["admin"])
get_current_owner = check_role(["owner", "admin"])
get_current_tenant = check_role(["tenant", "owner", "admin"])
get_current_maintenance = check_role(["maintenance", "admin"]) 