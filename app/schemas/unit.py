from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class UnitStatus(str, Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"
    reserved = "reserved"
    inactive = "inactive"

# Shared properties
class UnitBase(BaseModel):
    unit_number: Optional[str] = None
    floor: Optional[int] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    rent_amount: Optional[float] = None
    security_deposit: Optional[float] = None
    status: Optional[UnitStatus] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None

# Properties to receive on unit creation
class UnitCreate(UnitBase):
    unit_number: str
    bedrooms: float
    bathrooms: float
    square_feet: int
    rent_amount: float
    security_deposit: float
    status: UnitStatus = UnitStatus.available
    unit_images: Optional[List[str]] = None  # Base64 encoded images

# Properties to receive on unit update
class UnitUpdate(UnitBase):
    pass

# Properties shared by models stored in DB
class UnitInDBBase(UnitBase):
    unit_id: UUID
    property_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return to client
class Unit(UnitInDBBase):
    pass

# Unit with additional information for detailed view
class UnitWithDetails(Unit):
    property: Optional[dict] = None
    tenant: Optional[dict] = None
    lease: Optional[dict] = None
    images: List[str] = [] 