from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin, UUIDMixin, uuid_pk

class PropertyStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

class Property(Base, TimestampMixin):
    __tablename__ = "properties"
    
    property_id = uuid_pk("property_id")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
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
    status = Column(Enum(PropertyStatus), default=PropertyStatus.active)
    tax_id = Column(String)
    
    # Relationships
    owner = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="property", cascade="all, delete-orphan") 