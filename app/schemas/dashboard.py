from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class NotificationType(str, Enum):
    payment_due = "payment_due"
    lease_expiring = "lease_expiring"
    maintenance_update = "maintenance_update"
    document_verified = "document_verified"
    message_received = "message_received"
    system_alert = "system_alert"

class Notification(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool = False
    created_at: datetime
    data: Optional[Dict[str, Any]] = None
    
class NotificationsList(BaseModel):
    notifications: List[Notification]
    total_count: int
    unread_count: int

class PropertySummary(BaseModel):
    property_id: UUID
    name: str
    total_units: int
    occupied_units: int
    vacant_units: int
    total_monthly_income: float
    total_maintenance_requests: int

class LeaseSummary(BaseModel):
    lease_id: UUID
    property_name: str
    unit_number: str
    start_date: datetime
    end_date: datetime
    monthly_rent: float
    next_payment_date: datetime
    status: str

class PaymentSummary(BaseModel):
    payment_id: UUID
    amount: float
    status: str
    due_date: datetime
    paid_date: Optional[datetime] = None
    
class MaintenanceSummary(BaseModel):
    request_id: UUID
    title: str
    property_name: str
    unit_number: str
    status: str
    priority: str
    created_at: datetime
    last_updated: datetime

class OwnerDashboardStats(BaseModel):
    total_properties: int
    total_units: int
    occupied_units: int
    vacant_units: int
    occupancy_rate: float
    total_monthly_income: float
    outstanding_payments: float
    maintenance_requests_count: int
    properties: List[PropertySummary] = []
    recent_payments: List[PaymentSummary] = []
    upcoming_lease_expirations: List[LeaseSummary] = []
    maintenance_requests: List[MaintenanceSummary] = []

class TenantDashboardStats(BaseModel):
    lease: Optional[LeaseSummary] = None
    current_property: Optional[Dict[str, Any]] = None
    current_unit: Optional[Dict[str, Any]] = None
    next_payment_date: Optional[datetime] = None
    next_payment_amount: Optional[float] = None
    active_maintenance_requests: int = 0
    payment_history: List[PaymentSummary] = []
    maintenance_requests: List[MaintenanceSummary] = []

class DashboardSummary(BaseModel):
    account_status: str
    role: str
    owner_stats: Optional[OwnerDashboardStats] = None
    tenant_stats: Optional[TenantDashboardStats] = None
    recent_notifications: List[Notification] = [] 