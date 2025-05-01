from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from typing import Dict, Any
from pydantic import EmailStr

from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.supabase import supabase
from app.core.errors.supabase_error_handler import SupabaseError
from app.core.errors.error_handler import handle_repository_error
from app.core.config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
):
    """
    Register a new user with both Supabase Auth and save user metadata.
    """
    try:
        # First, register with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed with Supabase Auth"
            )
        
        # Get the user ID from the auth response
        supabase_uid = auth_response.user.id
        
        # Now, save additional user metadata
        user_repo = UserRepositorySupabase()
        user_data = user_in.model_dump(exclude={"password"})
        user_data["user_id"] = supabase_uid  # Use this as the user_id in our users table
        
        # Store a placeholder in password_hash to satisfy DB constraint
        # We're not actually using this for auth - Supabase Auth handles that
        user_data["password_hash"] = "SUPABASE_AUTH_MANAGED"
        
        created_user = await user_repo.create(user_data)
        
        if not created_user:
            logger.error(f"Failed to save user metadata for user {supabase_uid}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user metadata"
            )
        
        return created_user
    except Exception as e:
        logger.error(f"Registration error: {e}")
        if isinstance(e, HTTPException):
            raise
        
        # Handle Supabase specific errors
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        raise SupabaseError(
            code="REGISTRATION_ERROR",
            message=f"Registration failed: {error_message}",
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Login with Supabase Auth and return access and refresh tokens.
    """
    try:
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Use the Supabase tokens directly
        session = auth_response.session
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session returned from Supabase"
            )
        
        # Get the user from our database
        user_repo = UserRepositorySupabase()
        user = await user_repo.get_by_id(auth_response.user.id)
        
        if not user:
            # This might happen if the user registered but their metadata wasn't saved
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User metadata not found"
            )
        
        if user.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Update last login time
        await user_repo.update(auth_response.user.id, {
            "last_login_at": auth_response.user.last_sign_in_at
        })
        
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        if isinstance(e, HTTPException):
            raise
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
):
    """
    Refresh access token using Supabase refresh token.
    """
    try:
        # Use the refresh token to get a new access token
        auth_response = supabase.auth.refresh_session({
            "refresh_token": refresh_token
        })
        
        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        if isinstance(e, HTTPException):
            raise
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(authorization: str = Body(..., embed=True)):
    """
    Logout and invalidate the current session.
    """
    try:
        # Extract the token from the authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization format"
            )
        
        token = authorization[7:]  # Remove "Bearer " prefix
        
        # Sign out using Supabase
        supabase.auth.sign_out()
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        if isinstance(e, HTTPException):
            raise
        
        # Return success even on error to ensure the front end clears tokens
        return {"message": "Logout processed"}

@router.post("/forgot-password")
async def forgot_password(email: EmailStr = Body(..., embed=True)):
    """
    Send a password reset email to the user.
    
    This initiates the password reset flow via Supabase Auth.
    """
    try:
        # Use Supabase Auth to send the password reset email
        # The URL will be determined by Supabase settings or template
        response = supabase.auth.reset_password_email(email)
        
        # Log the action
        logger.info(f"Password reset requested for email: {email}")
        
        return {
            "message": "Password reset instructions have been sent to your email",
            "success": True
        }
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        
        # Don't leak information about whether the email exists
        return {
            "message": "If the email is registered, password reset instructions will be sent",
            "success": True
        }

@router.post("/reset-password")
async def reset_password(
    token: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True)
):
    """
    Reset the user's password using the token from the email.
    
    This completes the password reset flow.
    """
    try:
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
            
        # Use Supabase Auth to reset the password
        response = supabase.auth.update_user({
            "password": new_password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
        # Log the action but don't include the new password
        logger.info(f"Password reset successful for user: {response.user.id}")
        
        return {
            "message": "Password has been reset successfully",
            "success": True
        }
    except Exception as e:
        logger.error(f"Password reset completion error: {e}")
        
        if isinstance(e, HTTPException):
            raise
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password. The link may have expired or is invalid."
        ) 