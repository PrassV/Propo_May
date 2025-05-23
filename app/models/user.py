from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import relationship
import enum
import uuid
from app.models.base import Base, TimestampMixin

class UserRole(enum.Enum):
    owner = "owner"
    tenant = "tenant"
    maintenance = "maintenance"
    admin = "admin"

class UserStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(Enum(UserRole, native_enum=False), nullable=False)
    profile_picture_url = Column(String)
    email_verified = Column(Boolean, default=False)
    status = Column(Enum(UserStatus, native_enum=False), default=UserStatus.active)
    last_login_at = Column(TIMESTAMP(timezone=True))
    
    # Relationships
    properties = relationship("Property", back_populates="owner", cascade="all, delete-orphan")

    @staticmethod
    def from_dict(data: dict) -> 'User':
        """
        Convert a raw dictionary (e.g. from Supabase) into a User instance.
        Handles string-to-enum conversion.
        """
        data = data.copy()
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = UserRole(data['role'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = UserStatus(data['status'])
        return User(**data) 