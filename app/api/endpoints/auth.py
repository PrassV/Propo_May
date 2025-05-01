from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import ValidationError, EmailStr
from typing import Optional
from app.schemas.token import Token, TokenPayload
from app.schemas.user import User, UserCreate, UserBase
from app.core.security.auth import create_access_token, create_refresh_token
from app.db.session import get_db
from app.db.repositories.user_repository import UserRepository
from app.db.supabase import supabase
from app.api.dependencies.auth import get_current_active_user
from app.core.config.settings import settings
from uuid import UUID
import json

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
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
        
        # Create user in our database with the Supabase user ID
        user_data = user_in.model_dump(exclude={"password"})
        user_data["supabase_uid"] = supabase_response.user.id
        user_data["password_hash"] = "managed_by_supabase"  # We don't store the password
        
        user_repo = UserRepository(db)
        created_user = await user_repo.create(user_data)
        
        return created_user
    except Exception as e:
        # If we get an error from Supabase, it might be that the user already exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
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
        
        # Find the user in our database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_supabase_uid(supabase_response.user.id)
        
        if not user:
            # If user is in Supabase but not in our DB, create a minimal record
            user_data = {
                "email": supabase_response.user.email,
                "supabase_uid": supabase_response.user.id,
                "password_hash": "managed_by_supabase",
                "first_name": "",
                "last_name": "",
                "role": "tenant",  # Default role
            }
            user = await user_repo.create(user_data)
        
        if user.status.value != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )
        
        # Our custom token logic for session management
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        return {
            "access_token": supabase_response.session.access_token,
            "refresh_token": supabase_response.session.refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_active_user)
):
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.replace("Bearer ", "")
            supabase.auth.sign_out()
            return {"message": "Successfully logged out"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}"
            )
    
    return {"message": "Successfully logged out"} 