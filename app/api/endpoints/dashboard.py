from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from app.db.supabase import supabase
from app.schemas.dashboard import DashboardSummary, OwnerDashboardStats, TenantDashboardStats, NotificationsList
from app.api.dependencies.auth import get_current_active_user, get_active_role
from app.core.errors.error_handler import handle_repository_error
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    request: Request,
    current_user = Depends(get_current_active_user)
):
    """
    Get dashboard summary based on user's active role.
    
    This endpoint returns different data depending on whether the user
    is viewing as an owner, tenant, maintenance staff or admin.
    """
    try:
        user_id = current_user.get("user_id")
        active_role = get_active_role(request)
        
        # Prepare the base response
        response = {
            "account_status": current_user.get("status"),
            "role": active_role,
            "recent_notifications": await get_recent_notifications(user_id, 5)
        }
        
        # Add role-specific dashboard data
        if active_role == "owner" or active_role == "admin":
            owner_stats = await get_owner_dashboard_stats(user_id)
            response["owner_stats"] = owner_stats
            
        if active_role == "tenant" or (active_role == "owner" and current_user.get("is_also_tenant")):
            tenant_stats = await get_tenant_dashboard_stats(user_id)
            response["tenant_stats"] = tenant_stats
            
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving dashboard summary: {e}")
        handle_repository_error("fetch", "dashboard data", e)

@router.get("/notifications", response_model=NotificationsList)
async def get_notifications(
    current_user = Depends(get_current_active_user),
    unread_only: bool = Query(False),
    limit: int = Query(20),
    offset: int = Query(0)
):
    """
    Get user notifications with pagination and filtering options.
    """
    try:
        user_id = current_user.get("user_id")
        
        # Query to get notifications
        query = supabase.table("notifications").select("*").eq("user_id", user_id)
        
        # Filter by read status if requested
        if unread_only:
            query = query.eq("is_read", False)
            
        # Apply pagination
        query = query.order("created_at", options={"ascending": False}).range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        
        # Get total and unread counts
        count_query = supabase.table("notifications").select("id", "is_read").eq("user_id", user_id).execute()
        total_count = len(count_query.data) if count_query.data else 0
        unread_count = sum(1 for item in count_query.data if not item.get("is_read", True)) if count_query.data else 0
        
        return {
            "notifications": response.data or [],
            "total_count": total_count,
            "unread_count": unread_count
        }
        
    except Exception as e:
        logger.error(f"Error retrieving notifications: {e}")
        handle_repository_error("fetch", "notifications", e)

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user = Depends(get_current_active_user)
):
    """
    Mark a notification as read.
    """
    try:
        user_id = current_user.get("user_id")
        
        # First verify this notification belongs to the user
        notification = supabase.table("notifications").select("*").eq("id", str(notification_id)).eq("user_id", user_id).execute()
        
        if not notification.data or len(notification.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update the notification
        supabase.table("notifications").update({"is_read": True}).eq("id", str(notification_id)).execute()
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        handle_repository_error("update", "notification", e)

# Helper functions

async def get_recent_notifications(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent notifications for the user"""
    try:
        response = supabase.table("notifications").select("*").eq("user_id", user_id).order("created_at", options={"ascending": False}).limit(limit).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching recent notifications: {e}")
        return []

async def get_owner_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get dashboard statistics for property owners"""
    try:
        # Get properties owned by the user
        properties = supabase.table("properties").select("*").eq("owner_id", user_id).execute()
        
        if not properties.data:
            return {
                "total_properties": 0,
                "total_units": 0,
                "occupied_units": 0,
                "vacant_units": 0,
                "occupancy_rate": 0,
                "total_monthly_income": 0,
                "outstanding_payments": 0,
                "maintenance_requests_count": 0,
                "properties": [],
                "recent_payments": [],
                "upcoming_lease_expirations": [],
                "maintenance_requests": []
            }
            
        property_ids = [p.get("property_id") for p in properties.data]
        
        # Get units for these properties
        units_query = ",".join([f"'{pid}'" for pid in property_ids])
        units = supabase.table("units").select("*").filter("property_id", "in", f"({units_query})").execute()
        
        # Calculate statistics
        total_properties = len(properties.data)
        total_units = len(units.data) if units.data else 0
        occupied_units = sum(1 for unit in units.data if unit.get("status") == "occupied") if units.data else 0
        vacant_units = total_units - occupied_units
        occupancy_rate = (occupied_units / total_units) * 100 if total_units > 0 else 0
        
        # Calculate income
        total_monthly_income = sum(float(unit.get("rent_amount", 0)) for unit in units.data if unit.get("status") == "occupied") if units.data else 0
        
        # Get maintenance requests
        maintenance_requests = supabase.table("maintenance_requests").select("*").filter("property_id", "in", f"({units_query})").order("created_at", options={"ascending": False}).limit(5).execute()
        
        # Get recent payments
        recent_payments = supabase.table("payments").select("*").filter("property_id", "in", f"({units_query})").order("paid_date", options={"ascending": False}).limit(5).execute()
        
        # Get upcoming lease expirations
        today = datetime.now().date()
        sixty_days_later = today + timedelta(days=60)
        leases = supabase.table("leases").select("*").filter("property_id", "in", f"({units_query})").filter("end_date", "gte", today.isoformat()).filter("end_date", "lte", sixty_days_later.isoformat()).order("end_date").limit(5).execute()
        
        # Calculate outstanding payments
        outstanding_payments = supabase.table("payments").select("*").filter("property_id", "in", f"({units_query})").eq("status", "pending").execute()
        outstanding_amount = sum(float(payment.get("amount", 0)) for payment in outstanding_payments.data) if outstanding_payments.data else 0
        
        # Prepare property summaries
        property_summaries = []
        for property_data in properties.data:
            property_units = [u for u in units.data if u.get("property_id") == property_data.get("property_id")] if units.data else []
            property_occupied_units = sum(1 for u in property_units if u.get("status") == "occupied")
            property_monthly_income = sum(float(u.get("rent_amount", 0)) for u in property_units if u.get("status") == "occupied")
            
            property_maintenance_requests = [mr for mr in maintenance_requests.data if mr.get("property_id") == property_data.get("property_id")] if maintenance_requests.data else []
            
            property_summaries.append({
                "property_id": property_data.get("property_id"),
                "name": property_data.get("name"),
                "total_units": len(property_units),
                "occupied_units": property_occupied_units,
                "vacant_units": len(property_units) - property_occupied_units,
                "total_monthly_income": property_monthly_income,
                "total_maintenance_requests": len(property_maintenance_requests)
            })
        
        return {
            "total_properties": total_properties,
            "total_units": total_units,
            "occupied_units": occupied_units,
            "vacant_units": vacant_units,
            "occupancy_rate": occupancy_rate,
            "total_monthly_income": total_monthly_income,
            "outstanding_payments": outstanding_amount,
            "maintenance_requests_count": len(maintenance_requests.data) if maintenance_requests.data else 0,
            "properties": property_summaries,
            "recent_payments": recent_payments.data or [],
            "upcoming_lease_expirations": leases.data or [],
            "maintenance_requests": maintenance_requests.data or []
        }
    except Exception as e:
        logger.error(f"Error fetching owner dashboard stats: {e}")
        # Return minimal data on error
        return {
            "total_properties": 0,
            "total_units": 0,
            "occupied_units": 0,
            "vacant_units": 0,
            "occupancy_rate": 0,
            "total_monthly_income": 0,
            "outstanding_payments": 0,
            "maintenance_requests_count": 0
        }

async def get_tenant_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """Get dashboard statistics for tenants"""
    try:
        # Get active lease for this tenant
        lease = supabase.table("leases").select("*").eq("tenant_id", user_id).eq("status", "active").execute()
        
        if not lease.data or len(lease.data) == 0:
            return {
                "lease": None,
                "current_property": None,
                "current_unit": None,
                "next_payment_date": None,
                "next_payment_amount": None,
                "active_maintenance_requests": 0,
                "payment_history": [],
                "maintenance_requests": []
            }
            
        lease_data = lease.data[0]
        unit_id = lease_data.get("unit_id")
        property_id = lease_data.get("property_id")
        
        # Get unit details
        unit = supabase.table("units").select("*").eq("unit_id", unit_id).execute()
        unit_data = unit.data[0] if unit.data else None
        
        # Get property details
        property_data = supabase.table("properties").select("*").eq("property_id", property_id).execute()
        property_details = property_data.data[0] if property_data.data else None
        
        # Get maintenance requests
        maintenance_requests = supabase.table("maintenance_requests").select("*").eq("unit_id", unit_id).order("created_at", options={"ascending": False}).execute()
        active_maintenance_requests = [mr for mr in maintenance_requests.data if mr.get("status") in ["open", "assigned", "in_progress"]] if maintenance_requests.data else []
        
        # Get payment history
        payments = supabase.table("payments").select("*").eq("lease_id", lease_data.get("lease_id")).order("due_date", options={"ascending": False}).execute()
        
        # Calculate next payment date and amount
        today = datetime.now().date()
        next_payment = None
        for payment in payments.data if payments.data else []:
            due_date = datetime.fromisoformat(payment.get("due_date").replace("Z", "+00:00")).date()
            if due_date >= today and payment.get("status") in ["pending", "late"]:
                next_payment = payment
                break
        
        return {
            "lease": lease_data,
            "current_property": property_details,
            "current_unit": unit_data,
            "next_payment_date": next_payment.get("due_date") if next_payment else None,
            "next_payment_amount": float(next_payment.get("amount", 0)) if next_payment else None,
            "active_maintenance_requests": len(active_maintenance_requests),
            "payment_history": payments.data[:5] if payments.data else [],
            "maintenance_requests": maintenance_requests.data[:5] if maintenance_requests.data else []
        }
    except Exception as e:
        logger.error(f"Error fetching tenant dashboard stats: {e}")
        # Return minimal data on error
        return {
            "lease": None,
            "current_property": None,
            "current_unit": None,
            "next_payment_date": None,
            "next_payment_amount": None,
            "active_maintenance_requests": 0
        } 