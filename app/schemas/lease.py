from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum

class LeaseStatus(str, Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    terminated = "terminated"
    renewed = "renewed"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    late = "late"
    partial = "partial"
    waived = "waived"
    refunded = "refunded"

class PaymentType(str, Enum):
    rent = "rent"
    security_deposit = "security_deposit"
    application_fee = "application_fee"
    late_fee = "late_fee"
    maintenance_fee = "maintenance_fee"
    utility = "utility"
    other = "other"

class PaymentMethod(str, Enum):
    credit_card = "credit_card"
    bank_transfer = "bank_transfer"
    check = "check"
    cash = "cash"
    online_payment = "online_payment"
    other = "other"

class LeaseBase(BaseModel):
    unit_id: UUID
    start_date: date
    end_date: date
    rent_amount: float
    security_deposit: float
    payment_day: int = Field(..., ge=1, le=31, description="Day of month rent is due")
    terms: str

class LeaseCreate(LeaseBase):
    tenant_id: UUID
    is_auto_renew: bool = False
    lease_type: str = "standard"
    additional_fees: Optional[Dict[str, float]] = None
    deposit_refundable: bool = True

class LeaseUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[float] = None
    security_deposit: Optional[float] = None
    payment_day: Optional[int] = Field(None, ge=1, le=31)
    terms: Optional[str] = None
    status: Optional[LeaseStatus] = None
    is_auto_renew: Optional[bool] = None
    termination_reason: Optional[str] = None
    termination_date: Optional[date] = None

class LeaseDetail(BaseModel):
    lease_id: UUID
    unit_id: UUID
    property_id: UUID
    property_name: str
    unit_number: str
    tenant_id: UUID
    tenant_name: str
    tenant_email: str
    tenant_phone: Optional[str] = None
    start_date: date
    end_date: date
    rent_amount: float
    security_deposit: float
    payment_day: int
    status: LeaseStatus
    terms: str
    is_auto_renew: bool
    lease_type: str
    created_at: datetime
    updated_at: datetime
    termination_reason: Optional[str] = None
    termination_date: Optional[date] = None
    deposit_refundable: bool
    documents: List[Dict[str, Any]] = []
    additional_fees: Dict[str, float] = {}

class PaymentBase(BaseModel):
    lease_id: UUID
    amount: float
    payment_type: PaymentType
    description: Optional[str] = None
    due_date: date

class PaymentCreate(PaymentBase):
    payment_method: Optional[PaymentMethod] = None
    paid_amount: Optional[float] = None
    paid_date: Optional[date] = None
    is_late: bool = False
    late_fee: Optional[float] = None

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_type: Optional[PaymentType] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    paid_amount: Optional[float] = None
    paid_date: Optional[date] = None
    status: Optional[PaymentStatus] = None
    is_late: Optional[bool] = None
    late_fee: Optional[float] = None
    notes: Optional[str] = None

class PaymentDetail(BaseModel):
    payment_id: UUID
    lease_id: UUID
    tenant_id: UUID
    tenant_name: str
    property_id: UUID
    property_name: str
    unit_id: UUID
    unit_number: str
    amount: float
    payment_type: PaymentType
    description: Optional[str] = None
    due_date: date
    payment_method: Optional[PaymentMethod] = None
    paid_amount: Optional[float] = None
    paid_date: Optional[date] = None
    status: PaymentStatus
    is_late: bool
    late_fee: Optional[float] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime 