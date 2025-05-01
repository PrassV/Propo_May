from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.supabase import supabase
from app.schemas.user import User, UserCreate, UserUpdate
from app.db.repositories.user_repository import UserRepository
from app.api.dependencies.auth import get_current_active_user, get_current_admin

router = APIRouter()

@router.get("/me", response_model=Dict[str, Any])
async def read_current_user(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
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
            "id": str(current_user.id),
            "supabase_id": current_user.supabase_uid,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone": current_user.phone,
            "role": current_user.role.value,
            "profile_picture_url": current_user.profile_picture_url,
            "email_verified": session.user.email_confirmed_at is not None,
            "status": current_user.status.value,
            "last_login_at": session.user.last_sign_in_at,
            "created_at": str(current_user.created_at),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user data: {str(e)}"
        )

@router.put("/me", response_model=Dict[str, Any])
async def update_current_user(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update the current user's information.
    Updates both Supabase auth and our database.
    """
    try:
        user_repo = UserRepository(db)
        user_data = user_in.model_dump(exclude_unset=True)
        
        # Update user data in our database
        updated_user = await user_repo.update(current_user.id, user_data)
        
        # If email is being updated, update it in Supabase too
        if "email" in user_data:
            # Note: In a real implementation, you'd want to verify the new email
            # This is a simplified version
            supabase.auth.admin.update_user_by_id(
                current_user.supabase_uid,
                {"email": user_data["email"]}
            )
        
        # Return updated user data
        return {
            "id": str(updated_user.id),
            "supabase_id": updated_user.supabase_uid,
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "phone": updated_user.phone,
            "role": updated_user.role.value,
            "profile_picture_url": updated_user.profile_picture_url,
            "email_verified": updated_user.email_verified,
            "status": updated_user.status.value,
            "created_at": str(updated_user.created_at),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user data: {str(e)}"
        )

@router.get("", response_model=List[Dict[str, Any]])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin),  # Only admins can list all users
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None
):
    """
    List all users (admin only).
    """
    try:
        user_repo = UserRepository(db)
        users = await user_repo.list(skip=skip, limit=limit, role=role)
        
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "role": user.role.value,
                "profile_picture_url": user.profile_picture_url,
                "email_verified": user.email_verified,
                "status": user.status.value,
                "created_at": str(user.created_at),
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        ) 