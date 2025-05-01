from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.db.supabase import supabase
from app.schemas.user import User, UserCreate, UserUpdate
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.api.dependencies.auth import get_current_active_user, get_current_admin

router = APIRouter()

@router.get("/me", response_model=Dict[str, Any])
async def read_current_user(
    current_user = Depends(get_current_active_user)
):
    """
    Get information about the currently authenticated user.
    Combines data from Supabase auth and our database.
    """
    try:
        # Get user from Supabase
        session = supabase.auth.get_session()
        
        if not session or not session.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Return combined data
        return {
            "id": current_user.get("user_id"),
            "email": current_user.get("email"),
            "first_name": current_user.get("first_name"),
            "last_name": current_user.get("last_name"),
            "phone": current_user.get("phone"),
            "role": current_user.get("role"),
            "profile_picture_url": current_user.get("profile_picture_url"),
            "email_verified": session.user.email_confirmed_at is not None,
            "status": current_user.get("status"),
            "last_login_at": session.user.last_sign_in_at,
            "created_at": current_user.get("created_at"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user data: {str(e)}"
        )

@router.put("/me", response_model=Dict[str, Any])
async def update_current_user(
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Update the current user's information.
    Updates both Supabase auth and our database.
    """
    try:
        user_repo = UserRepositorySupabase()
        user_data = user_in.model_dump(exclude_unset=True)
        
        # Update user data in our database
        user_id = current_user.get("user_id")
        updated_user = await user_repo.update(user_id, user_data)
        
        # If email is being updated, update it in Supabase too
        if "email" in user_data:
            # Note: In a real implementation, you'd want to verify the new email
            # This is a simplified version
            supabase.auth.admin.update_user_by_id(
                user_id,
                {"email": user_data["email"]}
            )
        
        # Return updated user data
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user data: {str(e)}"
        )

@router.get("", response_model=List[Dict[str, Any]])
async def list_users(
    current_user = Depends(get_current_admin),  # Only admins can list all users
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None
):
    """
    List all users (admin only).
    """
    try:
        user_repo = UserRepositorySupabase()
        users = await user_repo.list(skip=skip, limit=limit, role=role)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        ) 