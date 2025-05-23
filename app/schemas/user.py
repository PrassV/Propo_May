from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    owner = "owner"
    tenant = "tenant"
    maintenance = "maintenance"
    admin = "admin"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"Invalid UserRole: {value}")

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"Invalid UserStatus: {value}")

class VerificationStatus(str, Enum):
    not_submitted = "not_submitted"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

    @classmethod
    def _missing_(cls, value):
        raise ValueError(f"Invalid VerificationStatus: {value}")

class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str = "USA"

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    profile_picture_url: Optional[str] = None
    status: Optional[UserStatus] = None

# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @field_validator('role')
    def validate_role(cls, v):
        if not isinstance(v, UserRole):
            raise ValueError(f"Role must be one of: {', '.join([r.value for r in UserRole])}")
        return v

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    role: Optional[UserRole] = None

    @field_validator('status')
    def validate_status(cls, v):
        if v is not None and not isinstance(v, UserStatus):
            raise ValueError(f"Status must be one of: {', '.join([s.value for s in UserStatus])}")
        return v

# User profile setup after registration
class UserProfileSetup(BaseModel):
    first_name: str
    last_name: str
    phone: str
    address: AddressSchema
    preferred_role: UserRole
    date_of_birth: Optional[datetime] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

# Role switching request
class RoleSwitchRequest(BaseModel):
    role: UserRole = Field(..., description="Role to switch to (owner or tenant)")

# Document verification
class VerificationDocumentSubmit(BaseModel):
    document_type: str = Field(..., description="Type of document (id, address_proof, income_proof)")
    description: Optional[str] = None

# Response model for user profile
class UserProfile(BaseModel):
    user_id: UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    available_roles: List[UserRole]
    profile_picture_url: Optional[str] = None
    status: UserStatus
    verification_status: VerificationStatus
    address: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    user_id: UUID
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    password_hash: str 