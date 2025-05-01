from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.db.supabase import supabase
from app.schemas.maintenance import (
    MaintenanceRequestCreate, 
    MaintenanceRequestUpdate, 
    MaintenanceRequestDetail,
    MaintenanceComment
)
from app.api.dependencies.auth import (
    get_current_active_user, 
    get_current_admin, 
    get_current_owner,
    get_current_tenant,
    get_current_maintenance,
    get_active_role
)
from app.core.errors.error_handler import handle_repository_error, handle_not_found_error
from app.utils.serializers import serialize_for_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    current_user = Depends(get_current_tenant)
):
    """
    Create a new maintenance request.
    
    This endpoint allows tenants to submit maintenance requests for their units.
    """
    try:
        user_id = current_user.get("user_id")
        
        # First, verify the unit belongs to the tenant
        # In a real implementation, you would check if the tenant has an active lease for this unit
        unit = supabase.table("units").select("*").eq("unit_id", str(request_data.unit_id)).execute()
        
        if not unit.data or len(unit.data) == 0:
            handle_not_found_error("unit", request_data.unit_id)
        
        unit_data = unit.data[0]
        property_id = unit_data.get("property_id")
        
        # Get property info
        property_data = supabase.table("properties").select("*").eq("property_id", property_id).execute()
        
        if not property_data.data or len(property_data.data) == 0:
            handle_not_found_error("property", property_id)
        
        # Create the maintenance request
        maintenance_data = {
            "request_id": str(UUID(int=0).int), # Will be auto-generated
            "unit_id": str(request_data.unit_id),
            "property_id": property_id,
            "tenant_id": user_id,
            "title": request_data.title,
            "description": request_data.description,
            "category": request_data.category.value,
            "priority": request_data.priority.value,
            "status": "open",
            "access_instructions": request_data.access_instructions,
            "scheduled_date": request_data.scheduled_date,
            "created_at": {"__type": "timestamp", "value": "now()"},
            "updated_at": {"__type": "timestamp", "value": "now()"}
        }
        
        # Filter out None values
        maintenance_data = {k: v for k, v in maintenance_data.items() if v is not None}
        
        # Serialize any datetime objects
        maintenance_data = serialize_for_supabase(maintenance_data)
        
        # Create the request
        response = supabase.table("maintenance_requests").insert(maintenance_data).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create maintenance request"
            )
            
        created_request = response.data[0]
        
        # Create notification for property owner
        owner_id = property_data.data[0].get("owner_id")
        
        notification_data = {
            "user_id": owner_id,
            "type": "maintenance_update",
            "title": "New Maintenance Request",
            "message": f"New maintenance request: {request_data.title}",
            "is_read": False,
            "created_at": {"__type": "timestamp", "value": "now()"},
            "data": {
                "request_id": created_request.get("request_id"),
                "property_id": property_id,
                "unit_id": str(request_data.unit_id)
            }
        }
        
        # Serialize notification data
        notification_data = serialize_for_supabase(notification_data)
        
        # Create notification
        supabase.table("notifications").insert(notification_data).execute()
        
        return {
            "message": "Maintenance request created successfully",
            "request": created_request
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating maintenance request: {e}")
        handle_repository_error("create", "maintenance request", e)

@router.get("", response_model=List[Dict[str, Any]])
async def list_maintenance_requests(
    request: Request,
    current_user = Depends(get_current_active_user),
    status: Optional[str] = Query(None),
    property_id: Optional[UUID] = Query(None),
    unit_id: Optional[UUID] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """
    List maintenance requests with role-based filtering:
    - Tenants: Only see their own requests
    - Owners: See requests for their properties
    - Maintenance staff: See requests assigned to them
    - Admins: See all requests
    """
    try:
        user_id = current_user.get("user_id")
        active_role = get_active_role(request)
        
        # Start building the query
        query = supabase.table("maintenance_requests").select("*")
        
        # Apply role-based filtering
        if active_role == "tenant":
            # Tenants only see their own requests
            query = query.eq("tenant_id", user_id)
        elif active_role == "owner":
            # Owners see requests for their properties
            if property_id:
                query = query.eq("property_id", str(property_id))
            else:
                # Get all properties owned by this user
                properties = supabase.table("properties").select("property_id").eq("owner_id", user_id).execute()
                
                if properties.data and len(properties.data) > 0:
                    property_ids = [p.get("property_id") for p in properties.data]
                    property_ids_str = ",".join([f"'{pid}'" for pid in property_ids])
                    query = query.filter("property_id", "in", f"({property_ids_str})")
                else:
                    # No properties, return empty list
                    return []
                    
        elif active_role == "maintenance":
            # Maintenance staff see requests assigned to them
            query = query.eq("assigned_to", user_id)
            
        # Admin sees all requests, so no additional filtering needed
        
        # Apply additional filters
        if status:
            query = query.eq("status", status)
            
        if unit_id:
            query = query.eq("unit_id", str(unit_id))
            
        # Apply pagination
        query = query.order("created_at", options={"ascending": False}).range(skip, skip + limit - 1)
        
        # Execute query
        response = query.execute()
        
        return response.data or []
        
    except Exception as e:
        logger.error(f"Error listing maintenance requests: {e}")
        handle_repository_error("fetch", "maintenance requests", e)

@router.get("/{request_id}", response_model=Dict[str, Any])
async def get_maintenance_request(
    request_id: UUID,
    request: Request,
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed maintenance request information.
    
    Access is role-based:
    - Tenants: Can only view their own requests
    - Owners: Can view requests for their properties
    - Maintenance: Can view requests assigned to them
    - Admins: Can view all requests
    """
    try:
        user_id = current_user.get("user_id")
        active_role = get_active_role(request)
        
        # Get the maintenance request
        response = supabase.table("maintenance_requests").select("*").eq("request_id", str(request_id)).execute()
        
        if not response.data or len(response.data) == 0:
            handle_not_found_error("maintenance request", request_id)
            
        maintenance_request = response.data[0]
        
        # Check if user has permission to view this request
        if active_role == "tenant" and maintenance_request.get("tenant_id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this maintenance request"
            )
            
        if active_role == "owner":
            # Check if the property belongs to this owner
            property_id = maintenance_request.get("property_id")
            property_data = supabase.table("properties").select("*").eq("property_id", property_id).eq("owner_id", user_id).execute()
            
            if not property_data.data or len(property_data.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to view this maintenance request"
                )
                
        if active_role == "maintenance" and maintenance_request.get("assigned_to") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this maintenance request"
            )
            
        # Get additional data to enrich the response
        property_id = maintenance_request.get("property_id")
        unit_id = maintenance_request.get("unit_id")
        tenant_id = maintenance_request.get("tenant_id")
        assigned_to = maintenance_request.get("assigned_to")
        
        # Get property and unit info
        property_data = supabase.table("properties").select("*").eq("property_id", property_id).execute()
        unit_data = supabase.table("units").select("*").eq("unit_id", unit_id).execute()
        
        # Get tenant info if present
        tenant_data = None
        if tenant_id:
            tenant_response = supabase.table("users").select("*").eq("user_id", tenant_id).execute()
            if tenant_response.data and len(tenant_response.data) > 0:
                tenant_data = tenant_response.data[0]
                
        # Get assigned staff info if present
        assigned_staff_data = None
        if assigned_to:
            staff_response = supabase.table("users").select("*").eq("user_id", assigned_to).execute()
            if staff_response.data and len(staff_response.data) > 0:
                assigned_staff_data = staff_response.data[0]
                
        # Get comments
        comments_response = supabase.table("maintenance_comments").select("*").eq("request_id", str(request_id)).order("created_at").execute()
        
        # Enrich the response
        detailed_request = dict(maintenance_request)
        
        # Add property and unit info
        if property_data.data and len(property_data.data) > 0:
            detailed_request["property_name"] = property_data.data[0].get("name")
            
        if unit_data.data and len(unit_data.data) > 0:
            detailed_request["unit_number"] = unit_data.data[0].get("unit_number")
            
        # Add tenant info
        if tenant_data:
            detailed_request["tenant_name"] = f"{tenant_data.get('first_name')} {tenant_data.get('last_name')}"
            detailed_request["tenant_phone"] = tenant_data.get("phone")
            
        # Add assigned staff info
        if assigned_staff_data:
            detailed_request["assigned_to_name"] = f"{assigned_staff_data.get('first_name')} {assigned_staff_data.get('last_name')}"
            
        # Add comments
        detailed_request["comments"] = comments_response.data or []
        
        return detailed_request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting maintenance request: {e}")
        handle_repository_error("fetch", "maintenance request", e)

@router.patch("/{request_id}", response_model=Dict[str, Any])
async def update_maintenance_request(
    request_id: UUID,
    request_data: MaintenanceRequestUpdate,
    current_user = Depends(get_current_active_user)
):
    """
    Update a maintenance request.
    
    Different roles can update different fields:
    - Tenants: Can only update their own requests' description, access instructions
    - Owners: Can update status, priority, assign staff
    - Maintenance: Can update status, add notes, set completion date
    - Admins: Can update all fields
    """
    try:
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        # Get the maintenance request
        response = supabase.table("maintenance_requests").select("*").eq("request_id", str(request_id)).execute()
        
        if not response.data or len(response.data) == 0:
            handle_not_found_error("maintenance request", request_id)
            
        maintenance_request = response.data[0]
        
        # Check permission and prepare update data based on role
        update_data = {}
        
        if role == "tenant":
            # Tenants can only update their own requests
            if maintenance_request.get("tenant_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update this maintenance request"
                )
                
            # Tenants can only update certain fields
            if request_data.description is not None:
                update_data["description"] = request_data.description
                
            if request_data.access_instructions is not None:
                update_data["access_instructions"] = request_data.access_instructions
                
            if request_data.scheduled_date is not None:
                update_data["scheduled_date"] = request_data.scheduled_date
                
        elif role == "owner":
            # Owners can only update requests for their properties
            property_id = maintenance_request.get("property_id")
            property_data = supabase.table("properties").select("*").eq("property_id", property_id).eq("owner_id", user_id).execute()
            
            if not property_data.data or len(property_data.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update this maintenance request"
                )
                
            # Owners can update status, priority, assigned_to
            if request_data.status is not None:
                update_data["status"] = request_data.status.value
                
            if request_data.priority is not None:
                update_data["priority"] = request_data.priority.value
                
            if request_data.assigned_to is not None:
                update_data["assigned_to"] = str(request_data.assigned_to)
                
            if request_data.resolution_notes is not None:
                update_data["resolution_notes"] = request_data.resolution_notes
                
        elif role == "maintenance":
            # Maintenance staff can only update assigned requests
            if maintenance_request.get("assigned_to") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to update this maintenance request"
                )
                
            # Maintenance can update status, notes, completion date
            if request_data.status is not None:
                update_data["status"] = request_data.status.value
                
            if request_data.resolution_notes is not None:
                update_data["resolution_notes"] = request_data.resolution_notes
                
            if request_data.completion_date is not None:
                update_data["completion_date"] = request_data.completion_date
                
            if request_data.estimated_cost is not None:
                update_data["estimated_cost"] = request_data.estimated_cost
                
            if request_data.actual_cost is not None:
                update_data["actual_cost"] = request_data.actual_cost
                
        elif role == "admin":
            # Admins can update all fields
            update_dict = request_data.model_dump(exclude_unset=True)
            
            # Convert enum values to strings
            if "status" in update_dict and update_dict["status"] is not None:
                update_dict["status"] = update_dict["status"].value
                
            if "priority" in update_dict and update_dict["priority"] is not None:
                update_dict["priority"] = update_dict["priority"].value
                
            if "category" in update_dict and update_dict["category"] is not None:
                update_dict["category"] = update_dict["category"].value
                
            update_data = update_dict
        
        # Add updated_at timestamp
        update_data["updated_at"] = {"__type": "timestamp", "value": "now()"}
        
        # Serialize any datetime objects
        update_data = serialize_for_supabase(update_data)
        
        # Update the request
        update_response = supabase.table("maintenance_requests").update(update_data).eq("request_id", str(request_id)).execute()
        
        if not update_response.data or len(update_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update maintenance request"
            )
            
        updated_request = update_response.data[0]
        
        # Create notification for status updates
        if "status" in update_data:
            # Notify tenant
            tenant_id = maintenance_request.get("tenant_id")
            
            notification_data = {
                "user_id": tenant_id,
                "type": "maintenance_update",
                "title": "Maintenance Request Update",
                "message": f"Your maintenance request has been updated to: {update_data['status']}",
                "is_read": False,
                "created_at": {"__type": "timestamp", "value": "now()"},
                "data": {
                    "request_id": str(request_id),
                    "property_id": maintenance_request.get("property_id"),
                    "unit_id": maintenance_request.get("unit_id"),
                    "new_status": update_data["status"]
                }
            }
            
            # Serialize notification data
            notification_data = serialize_for_supabase(notification_data)
            
            # Create notification
            supabase.table("notifications").insert(notification_data).execute()
        
        return {
            "message": "Maintenance request updated successfully",
            "request": updated_request
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating maintenance request: {e}")
        handle_repository_error("update", "maintenance request", e)

@router.post("/{request_id}/comments", response_model=Dict[str, Any])
async def add_maintenance_comment(
    request_id: UUID,
    comment: str = Form(...),
    attachment: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_active_user)
):
    """
    Add a comment to a maintenance request.
    """
    try:
        user_id = current_user.get("user_id")
        role = current_user.get("role")
        
        # Get the maintenance request
        response = supabase.table("maintenance_requests").select("*").eq("request_id", str(request_id)).execute()
        
        if not response.data or len(response.data) == 0:
            handle_not_found_error("maintenance request", request_id)
            
        maintenance_request = response.data[0]
        
        # Check if user has permission to comment on this request
        has_permission = False
        
        if role == "admin":
            has_permission = True
        elif role == "tenant" and maintenance_request.get("tenant_id") == user_id:
            has_permission = True
        elif role == "maintenance" and maintenance_request.get("assigned_to") == user_id:
            has_permission = True
        elif role == "owner":
            # Check if property belongs to owner
            property_id = maintenance_request.get("property_id")
            property_data = supabase.table("properties").select("*").eq("property_id", property_id).eq("owner_id", user_id).execute()
            has_permission = property_data.data and len(property_data.data) > 0
            
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to comment on this maintenance request"
            )
            
        # Handle file upload if present
        photo_url = None
        if attachment and attachment.filename:
            file_extension = attachment.filename.split(".")[-1]
            storage_path = f"maintenance_comments/{request_id}/{user_id}_{datetime.now().timestamp()}.{file_extension}"
            
            # Read the file content
            file_content = await attachment.read()
            
            # Upload to Supabase Storage
            upload_response = supabase.storage.from_("maintenance_documents").upload(
                storage_path, 
                file_content,
                file_options={"content-type": attachment.content_type}
            )
            
            # Get the public URL
            photo_url = supabase.storage.from_("maintenance_documents").get_public_url(storage_path)
            
        # Create the comment
        user_name = f"{current_user.get('first_name')} {current_user.get('last_name')}"
        
        comment_data = {
            "request_id": str(request_id),
            "user_id": user_id,
            "user_name": user_name,
            "user_role": role,
            "comment": comment,
            "created_at": {"__type": "timestamp", "value": "now()"}
        }
        
        if photo_url:
            comment_data["photo_url"] = photo_url
            
        # Serialize comment data
        comment_data = serialize_for_supabase(comment_data)
        
        # Create the comment
        comment_response = supabase.table("maintenance_comments").insert(comment_data).execute()
        
        if not comment_response.data or len(comment_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add comment"
            )
            
        created_comment = comment_response.data[0]
        
        # Create notification for the other parties
        notify_user_id = None
        
        if role == "tenant":
            # Notify the owner or assigned maintenance staff
            if maintenance_request.get("assigned_to"):
                notify_user_id = maintenance_request.get("assigned_to")
            else:
                # Get property owner
                property_id = maintenance_request.get("property_id")
                property_data = supabase.table("properties").select("*").eq("property_id", property_id).execute()
                
                if property_data.data and len(property_data.data) > 0:
                    notify_user_id = property_data.data[0].get("owner_id")
        else:
            # Notify the tenant
            notify_user_id = maintenance_request.get("tenant_id")
            
        if notify_user_id:
            notification_data = {
                "user_id": notify_user_id,
                "type": "maintenance_update",
                "title": "New Comment on Maintenance Request",
                "message": f"New comment from {user_name}: {comment[:30]}...",
                "is_read": False,
                "created_at": {"__type": "timestamp", "value": "now()"},
                "data": {
                    "request_id": str(request_id),
                    "comment_id": created_comment.get("id"),
                    "comment_by": user_name,
                    "comment_role": role
                }
            }
            
            # Serialize notification data
            notification_data = serialize_for_supabase(notification_data)
            
            # Create notification
            supabase.table("notifications").insert(notification_data).execute()
        
        return {
            "message": "Comment added successfully",
            "comment": created_comment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment to maintenance request: {e}")
        handle_repository_error("create", "maintenance comment", e) 