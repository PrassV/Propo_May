from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class MaintenancePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    emergency = "emergency"

class MaintenanceStatus(str, Enum):
    open = "open"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class MaintenanceCategory(str, Enum):
    plumbing = "plumbing"
    electrical = "electrical"
    hvac = "hvac"
    appliance = "appliance"
    structural = "structural"
    pest_control = "pest_control"
    cleaning = "cleaning"
    other = "other"

class MaintenanceRequestBase(BaseModel):
    title: str
    description: str
    category: MaintenanceCategory
    priority: MaintenancePriority
    access_instructions: Optional[str] = None

class MaintenanceRequestCreate(MaintenanceRequestBase):
    unit_id: UUID
    scheduled_date: Optional[datetime] = None
    photos: Optional[List[str]] = None  # URLs to photos

class MaintenanceRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MaintenanceCategory] = None
    priority: Optional[MaintenancePriority] = None
    status: Optional[MaintenanceStatus] = None
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    completion_date: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    access_instructions: Optional[str] = None

class MaintenanceComment(BaseModel):
    request_id: UUID
    user_id: UUID
    user_name: str
    user_role: str
    comment: str
    created_at: datetime
    photo_urls: Optional[List[str]] = None

class MaintenanceRequestDetail(BaseModel):
    request_id: UUID
    unit_id: UUID
    property_id: UUID
    property_name: str
    unit_number: str
    tenant_id: Optional[UUID] = None
    tenant_name: Optional[str] = None
    tenant_phone: Optional[str] = None
    title: str
    description: str
    category: MaintenanceCategory
    priority: MaintenancePriority
    status: MaintenanceStatus
    created_at: datetime
    updated_at: datetime
    scheduled_date: Optional[datetime] = None
    access_instructions: Optional[str] = None
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    resolution_notes: Optional[str] = None
    completion_date: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    photos: List[str] = []
    comments: List[MaintenanceComment] = [] 