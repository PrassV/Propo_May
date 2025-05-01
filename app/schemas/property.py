from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class PropertyStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"

class Coordinates(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str = "USA"
    coordinates: Optional[Coordinates] = None

# Shared properties
class PropertyBase(BaseModel):
    name: Optional[str] = None
    property_type: Optional[str] = None
    year_built: Optional[int] = None
    total_units: Optional[int] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None

# Properties to receive on property creation
class PropertyCreate(BaseModel):
    name: str
    address: Address
    property_type: str
    year_built: Optional[int] = None
    total_units: int
    amenities: Optional[List[str]] = None
    description: Optional[str] = None
    property_image: Optional[str] = None  # Base64 encoded image

# Properties to receive on property update
class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    property_type: Optional[str] = None
    year_built: Optional[int] = None
    total_units: Optional[int] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None

# Properties shared by models stored in DB
class PropertyInDBBase(PropertyBase):
    property_id: UUID
    owner_id: UUID
    street: str
    city: str
    state: str
    zip: str
    country: str
    status: PropertyStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return to client
class Property(PropertyInDBBase):
    pass

# Property with additional information for detailed view
class PropertyWithDetails(Property):
    available_units: int
    occupied_units: int
    images: List[str] = []
    owner: Optional[dict] = None 