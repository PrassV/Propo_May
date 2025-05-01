from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import ValidationError, EmailStr
from typing import Optional, Dict, Any
from app.schemas.token import Token, TokenPayload
from app.schemas.user import User, UserCreate, UserBase
from app.core.security.auth import create_access_token, create_refresh_token
from app.db.session import get_db
from app.db.repositories.user_repository_supabase import UserRepositorySupabase
from app.db.supabase import supabase
from app.api.dependencies.auth import get_current_active_user
from app.core.config.settings import settings
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate
):
    """
    Register a new user with Supabase Auth and store user data in Supabase database.
    """
    try:
        # Create user in Supabase auth
        supabase_response = supabase.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
        })
        
        if not supabase_response or not supabase_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register user with Supabase"
            )
        
        # Create user in our Supabase database table
        user_repo = UserRepositorySupabase()
        user_data = user_in.model_dump(exclude={"password"})
        user_data["supabase_uid"] = supabase_response.user.id
        user_data["status"] = "active"
        
        created_user = await user_repo.create(user_data)
        
        # Return combined data
        return {
            "id": created_user.get("id"),
            "email": created_user.get("email"),
            "first_name": created_user.get("first_name"),
            "last_name": created_user.get("last_name"),
            "role": created_user.get("role"),
            "message": "User registered successfully. Please check your email for verification."
        }
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        # If we get an error from Supabase, it might be that the user already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user with Supabase Auth and return tokens.
    """
    try:
        # Authenticate with Supabase
        supabase_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password,
        })
        
        if not supabase_response or not supabase_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Get user from our database to check status
        user_repo = UserRepositorySupabase()
        user = await user_repo.get_by_supabase_uid(supabase_response.user.id)
        
        if not user:
            # If user is in Supabase but not in our DB, create a minimal record
            user_data = {
                "email": supabase_response.user.email,
                "supabase_uid": supabase_response.user.id,
                "first_name": "",
                "last_name": "",
                "role": "tenant",  # Default role
                "status": "active"
            }
            user = await user_repo.create(user_data)
        
        if user.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        
        # Return the Supabase tokens
        return {
            "access_token": supabase_response.session.access_token,
            "refresh_token": supabase_response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str
):
    """
    Refresh authentication token using Supabase.
    """
    try:
        # Refresh token with Supabase
        supabase_response = supabase.auth.refresh_session(refresh_token)
        
        if not supabase_response or not supabase_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
            
        return {
            "access_token": supabase_response.session.access_token,
            "refresh_token": supabase_response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Log out the current user by signing out from Supabase.
    """
    if authorization and authorization.startswith("Bearer "):
        try:
            supabase.auth.sign_out()
            return {"message": "Successfully logged out"}
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}"
            )
    
    return {"message": "Successfully logged out"} 