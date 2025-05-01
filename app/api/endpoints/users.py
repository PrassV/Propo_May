from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.db.supabase import supabase
from app.schemas.user import User, UserCreate, UserUpdate, UserProfileSetup, RoleSwitchRequest, VerificationDocumentSubmit
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.api.dependencies.auth import get_current_active_user, get_current_admin, get_user_available_roles, switch_role
from app.core.errors.error_handler import handle_repository_error, handle_validation_error
import logging

logger = logging.getLogger(__name__)
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

@router.post("/profile-setup", response_model=Dict[str, Any])
async def complete_profile(
    profile_data: UserProfileSetup,
    current_user = Depends(get_current_active_user)
):
    """
    Complete user profile with additional details after registration.
    Users can provide personal information and select their preferred role.
    """
    try:
        user_repo = UserRepositorySupabase()
        user_id = current_user.get("user_id")
        
        # Convert address to dict
        address_dict = profile_data.address.model_dump()
        
        # Create the user data to update
        user_data = {
            "first_name": profile_data.first_name,
            "last_name": profile_data.last_name,
            "phone": profile_data.phone,
            "address": address_dict,
            "role": profile_data.preferred_role,
            "profile_completed": True
        }
        
        # Include optional fields if provided
        if profile_data.date_of_birth:
            user_data["date_of_birth"] = profile_data.date_of_birth
            
        if profile_data.emergency_contact_name:
            user_data["emergency_contact_name"] = profile_data.emergency_contact_name
            
        if profile_data.emergency_contact_phone:
            user_data["emergency_contact_phone"] = profile_data.emergency_contact_phone
        
        # Update the user profile
        updated_user = await user_repo.update(user_id, user_data)
        
        # Return success message with updated user data
        return {
            "message": "Profile completed successfully",
            "user": updated_user
        }
    except Exception as e:
        logger.error(f"Error completing profile: {e}")
        handle_repository_error("update", "user profile", e)

@router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(
    current_user = Depends(get_current_active_user)
):
    """
    Get the current user's profile including available roles.
    """
    try:
        user_id = current_user.get("user_id")
        
        # Get available roles
        available_roles = await get_user_available_roles(user_id)
        
        # Add available roles to the profile
        profile_data = dict(current_user)
        profile_data["available_roles"] = available_roles
        
        # Check verification status
        verification_status = profile_data.get("verification_status", "not_submitted")
        profile_data["verification_status"] = verification_status
        
        return profile_data
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        handle_repository_error("fetch", "user profile", e)

@router.post("/switch-role", response_model=Dict[str, Any])
async def user_switch_role(
    request: Request,
    role_data: RoleSwitchRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Switch the user's active role.
    
    Users with multiple roles (e.g., both owner and tenant) can switch
    between their available roles to see different views of the system.
    """
    try:
        # Try to switch the role
        success = await switch_role(request, role_data.role, current_user)
        
        if success:
            return {
                "message": f"Successfully switched to {role_data.role} role",
                "current_role": role_data.role
            }
        else:
            handle_validation_error("user", "role", "Failed to switch role")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error switching role: {e}")
        handle_repository_error("update", "user role", e)

@router.post("/verification-documents", response_model=Dict[str, Any])
async def submit_verification_documents(
    document_data: VerificationDocumentSubmit,
    document: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """
    Submit verification documents for user account.
    
    Users can submit ID, proof of address, income verification, etc.
    """
    try:
        user_id = current_user.get("user_id")
        
        # Upload document to Supabase Storage
        file_extension = document.filename.split(".")[-1]
        storage_path = f"verification_documents/{user_id}/{document_data.document_type}.{file_extension}"
        
        # Read the file content
        file_content = await document.read()
        
        # Upload to Supabase Storage
        response = supabase.storage.from_("user_documents").upload(
            storage_path, 
            file_content,
            file_options={"content-type": document.content_type}
        )
        
        # Get the public URL
        document_url = supabase.storage.from_("user_documents").get_public_url(storage_path)
        
        # Update the user's verification status
        user_repo = UserRepositorySupabase()
        
        # Get existing documents or initialize
        user_data = await user_repo.get_by_id(user_id)
        verification_documents = user_data.get("verification_documents", [])
        
        # Add the new document
        verification_documents.append({
            "document_type": document_data.document_type,
            "description": document_data.description,
            "file_url": document_url,
            "submitted_at": {"__type": "timestamp", "value": "now()"},
            "status": "pending"
        })
        
        # Update the user record
        updated_user = await user_repo.update(user_id, {
            "verification_documents": verification_documents,
            "verification_status": "pending"
        })
        
        return {
            "message": "Document submitted successfully",
            "document_type": document_data.document_type,
            "status": "pending"
        }
    except Exception as e:
        logger.error(f"Error submitting verification document: {e}")
        handle_repository_error("upload", "verification document", e) 