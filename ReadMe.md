# Property Management Portal Project Setup Guide

This README provides instructions for setting up a complete property management portal with FastAPI and Supabase. Follow these steps in Cursor to quickly scaffold your project structure and implement CRUD operations.

## Project Overview

This property management portal is a full-stack application with:
- FastAPI backend
- Supabase for PostgreSQL database, authentication, and storage
- Async architecture using Python's asyncio
- React frontend (optional)

## Initial Setup

### 1. Create Project Structure

```bash
# Run these commands in your terminal to create the base structure
mkdir property-management-portal
cd property-management-portal

# Backend directories
mkdir -p app/{api,core,db,models,schemas,services,utils}
mkdir -p app/api/{dependencies,endpoints,middlewares}
mkdir -p app/core/{config,security}
mkdir -p app/db/{repositories,migrations}
touch app/__init__.py
touch app/main.py

# Create needed __init__.py files
touch app/api/__init__.py
touch app/core/__init__.py
touch app/db/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch app/api/dependencies/__init__.py
touch app/api/endpoints/__init__.py
touch app/api/middlewares/__init__.py
touch app/core/config/__init__.py
touch app/core/security/__init__.py
touch app/db/repositories/__init__.py

# Create essential configuration files
touch .env
touch .env.example
touch requirements.txt
touch README.md
```

### 2. Install Dependencies

Add the following to your `requirements.txt` file:

```
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.11.1
asyncpg>=0.27.0
supabase>=1.0.3
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
email-validator>=2.0.0
pytz>=2023.3
python-dotenv>=1.0.0
pydantic-settings>=2.0.0
pytest>=7.3.1
httpx>=0.24.1
```

Then run:

```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variables

Add the following to your `.env` and `.env.example` files (with appropriate values for `.env`):

```
# API Settings
API_V1_PREFIX=/api
PROJECT_NAME=Property Management Portal
DEBUG=True
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase Settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/property_management
```

## Project Structure Explanation

```
app/
├── api/                 # API layer
│   ├── dependencies/    # Dependency injection functions
│   ├── endpoints/       # API route handlers
│   └── middlewares/     # Custom middleware
├── core/                # Core application code
│   ├── config/          # Application configuration
│   └── security/        # Security utilities (JWT, password hashing)
├── db/                  # Database layer
│   ├── repositories/    # Database access logic
│   └── migrations/      # Alembic migrations
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic models for request/response validation
├── services/            # Business logic layer
├── utils/               # Utility functions
└── main.py              # Application entry point
```

## Implementation Steps

### 1. Set Up Core Configuration

Create `app/core/config/settings.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Property Management Portal"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. Set Up Database Connection

Create `app/db/session.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3. Create Base Models

Create `app/models/base.py`:

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class TimestampMixin:
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

### 4. Set Up Security

Create `app/core/security/auth.py`:

```python
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 5. Set Up Supabase Client

Create `app/db/supabase.py`:

```python
from supabase import create_client, Client
from app.core.config.settings import settings

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

supabase = get_supabase_client()
```

### 6. Create User Model Example

Create `app/models/user.py`:

```python
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import Base, TimestampMixin, UUIDMixin

class UserRole(enum.Enum):
    owner = "owner"
    tenant = "tenant"
    maintenance = "maintenance"
    admin = "admin"

class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    profile_picture_url = Column(String)
    email_verified = Column(Boolean, default=False)
    status = Column(Enum(UserStatus), default=UserStatus.active)
    last_login_at = Column(String)
```

### 7. Create User Schema Example

Create `app/schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    owner = "owner"
    tenant = "tenant"
    maintenance = "maintenance"
    admin = "admin"

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

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

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

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
```

### 8. Create User Repository Example

Create `app/db/repositories/user_repository.py`:

```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.user import User
from app.core.security.auth import get_password_hash, verify_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: dict) -> User:
        # Hash password if present
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        
        db_user = User(**user_data)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        # Hash password if present
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
            
        await self.db.execute(
            update(User).where(User.id == user_id).values(**user_data)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: UUID) -> None:
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
```

### 9. Create Authorization Dependencies

Create `app/api/dependencies/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.settings import settings
from app.db.session import get_db
from app.db.repositories.user_repository import UserRepository
from app.schemas.token import TokenPayload
from app.models.user import UserRole
from typing import Optional
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(token_data.sub))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user

def check_role(allowed_roles: list[UserRole]):
    async def _check_role(current_user = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permissions",
            )
        return current_user
    return _check_role

# Role-specific dependencies
get_current_admin = check_role([UserRole.admin])
get_current_owner = check_role([UserRole.owner, UserRole.admin])
get_current_maintenance = check_role([UserRole.maintenance, UserRole.admin])
```

### 10. Create Token Schema

Create `app/schemas/token.py`:

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: Optional[str] = None
```

### 11. Create Authentication Endpoint

Create `app/api/endpoints/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.core.security.auth import create_access_token, create_refresh_token
from app.db.session import get_db
from app.db.repositories.user_repository import UserRepository
from app.api.dependencies.auth import get_current_active_user
from app.core.config.settings import settings

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    existing_user = await user_repo.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_data = user_in.model_dump()
    created_user = await user_repo.create(user_data)
    return created_user

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user_repo = UserRepository(db)
    user = await user_repo.authenticate(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str, db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
        
        if token_data.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(token_data.sub))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    # In a real-world scenario, you might want to blacklist the token
    # For simplicity, we'll just return a success message
    return {"message": "Successfully logged out"}
```

### 12. Create API Router

Create `app/api/api.py`:

```python
from fastapi import APIRouter
from app.api.endpoints import auth, users, properties, units, applications, leases, maintenance, payments, documents

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# Include other routers as they are created:
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
# ... and so on
```

### 13. Create Main Application File

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config.settings import settings
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {"message": "Welcome to the Property Management Portal API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

## Creating CRUD Operations for Entities

For each entity in your system (Properties, Units, Leases, etc.), follow this pattern:

1. Create the SQLAlchemy model in `app/models/`
2. Create the Pydantic schemas in `app/schemas/`
3. Create the repository in `app/db/repositories/`
4. Create endpoints in `app/api/endpoints/`
5. Include the router in `app/api/api.py`

### Example for Property Entity

#### 1. Create SQLAlchemy Model (`app/models/property.py`):

```python
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base, TimestampMixin, UUIDMixin

class Property(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "properties"
    
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip = Column(String, nullable=False)
    country = Column(String, default="USA")
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    property_type = Column(String, nullable=False)
    year_built = Column(Integer)
    total_units = Column(Integer, nullable=False)
    amenities = Column(ARRAY(Text), default=[])
    description = Column(Text)
    status = Column(String, default="active")
    tax_id = Column(String)
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    property_images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
```

#### 2. Create Pydantic Schemas (`app/schemas/property.py`):

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Shared properties
class PropertyBase(BaseModel):
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = "USA"
    property_type: Optional[str] = None
    year_built: Optional[int] = None
    total_units: Optional[int] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None

# Properties to receive on property creation
class PropertyCreate(PropertyBase):
    name: str
    street: str
    city: str
    state: str
    zip: str
    property_type: str
    total_units: int
    
# Properties to receive on property update
class PropertyUpdate(PropertyBase):
    pass

# Properties shared by models stored in DB
class PropertyInDBBase(PropertyBase):
    property_id: UUID
    owner_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return to client
class Property(PropertyInDBBase):
    pass

# Properties properties stored in DB
class PropertyInDB(PropertyInDBBase):
    pass

# Property with additional information
class PropertyWithDetails(Property):
    available_units: int
    occupied_units: int
    images: List[str] = []
```

#### 3. Create Repository (`app/db/repositories/property_repository.py`):

```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.models.property import Property
from app.models.unit import Unit

class PropertyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, property_data: dict) -> Property:
        db_property = Property(**property_data)
        self.db.add(db_property)
        await self.db.commit()
        await self.db.refresh(db_property)
        return db_property
    
    async def get_by_id(self, property_id: UUID) -> Optional[Property]:
        result = await self.db.execute(select(Property).where(Property.id == property_id))
        return result.scalars().first()
    
    async def list(self, 
                  owner_id: Optional[UUID] = None, 
                  skip: int = 0, 
                  limit: int = 100,
                  city: Optional[str] = None,
                  state: Optional[str] = None,
                  property_type: Optional[str] = None) -> List[Property]:
        query = select(Property)
        
        if owner_id:
            query = query.where(Property.owner_id == owner_id)
        
        if city:
            query = query.where(Property.city.ilike(f"%{city}%"))
        
        if state:
            query = query.where(Property.state == state)
            
        if property_type:
            query = query.where(Property.property_type == property_type)
            
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, property_id: UUID, property_data: dict) -> Optional[Property]:
        await self.db.execute(
            update(Property).where(Property.id == property_id).values(**property_data)
        )
        await self.db.commit()
        return await self.get_by_id(property_id)
    
    async def delete(self, property_id: UUID) -> None:
        await self.db.execute(delete(Property).where(Property.id == property_id))
        await self.db.commit()
        
    async def get_with_unit_stats(self, property_id: UUID) -> dict:
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return None
            
        # Get unit statistics
        result = await self.db.execute(
            select(
                func.count(Unit.id).label("total_units"),
                func.sum(case((Unit.status == "available", 1), else_=0)).label("available_units"),
                func.sum(case((Unit.status == "occupied", 1), else_=0)).label("occupied_units")
            ).where(Unit.property_id == property_id)
        )
        
        stats = result.first()
        
        property_dict = {**property_obj.__dict__}
        property_dict["available_units"] = stats.available_units if stats.available_units else 0
        property_dict["occupied_units"] = stats.occupied_units if stats.occupied_units else 0
        
        return property_dict
```

#### 4. Create Endpoints (`app/api/endpoints/properties.py`):

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.property import Property, PropertyCreate, PropertyUpdate, PropertyWithDetails
from app.db.repositories.property_repository import PropertyRepository
from app.api.dependencies.auth import get_current_active_user, get_current_owner, get_current_admin

router = APIRouter()

@router.post("", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_in: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    property_data = property_in.model_dump()
    property_data["owner_id"] = current_user.id
    
    property_repo = PropertyRepository(db)
    created_property = await property_repo.create(property_data)
    return created_property

@router.get("", response_model=List[Property])
async def list_properties(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None
):
    property_repo = PropertyRepository(db)
    
    # Filter properties based on user role
    if current_user.role == "admin":
        # Admins can see all properties
        properties = await property_repo.list(
            skip=skip, limit=limit, city=city, state=state, property_type=property_type
        )
    elif current_user.role == "owner":
        # Owners can only see their properties
        properties = await property_repo.list(
            owner_id=current_user.id, skip=skip, limit=limit, 
            city=city, state=state, property_type=property_type
        )
    elif current_user.role == "maintenance":
        # Get properties assigned to maintenance user (implement this)
        # For now, return an empty list
        properties = []
    else:
        # Tenants can only see properties they're renting (implement this)
        # For now, return an empty list
        properties = []
        
    return properties

@router.get("/{property_id}", response_model=PropertyWithDetails)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    property_repo = PropertyRepository(db)
    property_with_stats = await property_repo.get_with_unit_stats(property_id)
    
    if not property_with_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user has permission to access this property
    if current_user.role != "admin" and (
        (current_user.role == "owner" and property_with_stats.owner_id != current_user.id) or
        (current_user.role == "tenant" or current_user.role == "maintenance")
        # For tenant and maintenance, add proper checks
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this property"
        )
        
    return property_with_stats

@router.patch("/{property_id}", response_model=Property)
async def update_property(
    property_id: UUID,
    property_in: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.role != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this property"
        )
    
    property_data = property_in.model_dump(exclude_unset=True)
    updated_property = await property_repo.update(property_id, property_data)
    return updated_property

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.role != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this property"
        )
    
    # Instead of hard delete, set status to deleted
    await property_repo.update(property_id, {"status": "deleted"})
    return None
```

#### 5. Include the Router in `app/api/api.py`:

```python
# Add to existing imports
from app.api.endpoints import properties

# Add to existing route includes
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
```

## Running the Application

Run your FastAPI application with:

```bash
uvicorn app.main:app --reload
```

Access the API documentation at API_doc.md

Here's a detailed project structure for implementing 100 endpoints with Supabase integration and automated testing:

property-management-portal/
├── .github/
│   └── workflows/
│       ├── ci-cd.yml          # GitHub Actions pipeline
│       └── security-scan.yml
├── alembic/                   # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── app/                       # Main application
│   ├── api/                   # All endpoint routers
│   │   ├── dependencies/      # Auth and access control
│   │   ├── endpoints/
│   │   │   ├── auth.py        # Endpoints 1-9
│   │   │   ├── properties.py  # Endpoints 10-21
│   │   │   ├── units.py       # Endpoints 22-34
│   │   │   └── ...            # Other endpoint groups
│   │   └── router.py          # Combined routes
│   ├── core/                  # Configuration and security
│   │   ├── config.py          # Settings class
│   │   └── security.py        # Auth utilities
│   ├── db/                    # Database layer
│   │   ├── repositories/      # CRUD operations
│   │   │   ├── user_repo.py
│   │   │   ├── property_repo.py
│   │   │   └── ...
│   │   └── session.py         # Supabase connection
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── property.py
│   │   └── ...
│   ├── schemas/               # Pydantic models
│   │   ├── auth.py
│   │   ├── property.py
│   │   └── ...
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   ├── property_service.py
│   │   └── ...
│   ├── utils/                 # Helpers
│   │   ├── storage.py         # Supabase storage
│   │   └── logger.py          # Structured logging
│   ├── main.py                # App entrypoint
│   └── dependencies.py        # Shared dependencies
├── tests/                     # Comprehensive tests
│   ├── conftest.py            # Pytest fixtures
│   ├── test_auth.py           # Tests for endpoints 1-9
│   ├── test_properties.py     # Tests for 10-21
│   └── ...                    # Other test modules
├── migrations/                # Supabase-specific migrations
├── scripts/                   # Utility scripts
│   ├── seed_db.py
│   └── generate_docs.py
├── .env                       # Environment variables
├── .env.example
├── .gitignore
├── alembic.ini                # Migration config
├── docker-compose.yml         # Local development
├── Dockerfile
├── requirements.txt           # Pinned dependencies
├── pyproject.toml             # Linting/config
├── pytest.ini                 # Test config
└── README.md                  # Setup/usage docs

Key File Contents:

app/core/config.py

python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DB_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    
    class Config:
        env_file = ".env"

settings = Settings()
app/db/session.py

python
from supabase import create_client
from app.core.config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def get_db():
    yield supabase
app/api/endpoints/auth.py

python
from fastapi import APIRouter, Depends
from app.schemas.auth import UserCreate, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, service: AuthService = Depends()):
    return await service.register_user(user_data)
tests/test_auth.py

python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_user_registration():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()
Essential Configuration Files:

requirements.txt

fastapi==0.110.0
uvicorn==0.29.0
supabase==2.3.1
pytest==8.1.1
pytest-asyncio==0.23.5
pytest-cov==4.1.0
python-dotenv==1.0.0
docker-compose.yml

yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: supabase/postgres:14.1.0
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
pytest.ini

ini
[pytest]
asyncio_mode = auto
testpaths = tests
addopts = -v --cov=app --cov-report=term-missing
Implementation Workflow:

Create base structure:

bash
mkdir -p app/{api/dependencies,endpoints,core,db/repositories,models,schemas,services,utils}
mkdir -p tests/{unit,integration} alembic/versions scripts
Set up testing environment:

bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest --cov # Verify initial setup
Implement in this order:

Core config and database setup

Models and schemas

Repository classes

Service layer

API endpoints

Test cases for each endpoint group

This structure supports:

Clean architecture with separation of concerns

Easy scalability for 100+ endpoints

Atomic test cases

CI/CD integration

Local and cloud development parity

Secure credential management

## Supabase Credential:
use Supabase for Authentication. Please find below Supabase credential in .env file

Use MCP server to communicate with supabase db.