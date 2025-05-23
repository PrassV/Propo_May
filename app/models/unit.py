from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
import uuid
from app.models.base import Base, TimestampMixin

class UnitStatus(enum.Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"
    reserved = "reserved"
    inactive = "inactive"

class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    
    unit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.property_id"), nullable=False)
    unit_number = Column(String, nullable=False)
    floor = Column(Integer)
    bedrooms = Column(Numeric(3, 1), nullable=False)
    bathrooms = Column(Numeric(3, 1), nullable=False)
    square_feet = Column(Integer, nullable=False)
    rent_amount = Column(Numeric(10, 2), nullable=False)
    security_deposit = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(UnitStatus, native_enum=False), default=UnitStatus.available)
    amenities = Column(ARRAY(Text), default=[])
    description = Column(Text)
    
    # Relationships
    property = relationship("Property", back_populates="units") 