from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.schemas.property import Property, PropertyCreate, PropertyUpdate, PropertyWithDetails
from app.db.repositories.property_repository_supabase import PropertyRepositorySupabase
from app.api.dependencies.auth import get_current_active_user, get_current_owner, get_current_admin
import json

router = APIRouter()

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_property(
    property_in: PropertyCreate,
    current_user = Depends(get_current_owner)
):
    """
    Create a new property with the provided data.
    - Only owners and admins can create properties
    - The current user is automatically set as the owner
    """
    property_data = {
        "owner_id": current_user.get("user_id"),
        "name": property_in.name,
        "street": property_in.address.street,
        "city": property_in.address.city,
        "state": property_in.address.state,
        "zip": property_in.address.zip,
        "country": property_in.address.country,
        "property_type": property_in.property_type,
        "year_built": property_in.year_built,
        "total_units": property_in.total_units,
        "amenities": property_in.amenities or [],
        "description": property_in.description
    }
    
    # Add coordinates if provided
    if property_in.address.coordinates:
        property_data["latitude"] = property_in.address.coordinates.latitude
        property_data["longitude"] = property_in.address.coordinates.longitude
    
    # TODO: Handle property_image upload to storage
    
    property_repo = PropertyRepositorySupabase()
    created_property = await property_repo.create(property_data)
    return created_property

@router.get("", response_model=List[Dict[str, Any]])
async def list_properties(
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None
):
    """
    List properties with optional filtering.
    - Admins can see all properties
    - Owners can only see their properties
    - Tenants can only see properties they're renting
    - Maintenance staff can only see properties assigned to them
    """
    property_repo = PropertyRepositorySupabase()
    
    # Filter properties based on user role
    if current_user.get("role") == "admin":
        # Admins can see all properties
        properties = await property_repo.list(
            skip=skip, limit=limit, city=city, state=state, property_type=property_type
        )
    elif current_user.get("role") == "owner":
        # Owners can only see their properties
        properties = await property_repo.list(
            owner_id=current_user.get("user_id"), skip=skip, limit=limit, 
            city=city, state=state, property_type=property_type
        )
    else:
        # For tenants and maintenance, we'll implement this later
        # For now, return an empty list
        properties = []
        
    return properties

@router.get("/{property_id}", response_model=Dict[str, Any])
async def get_property(
    property_id: UUID,
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific property.
    - Admins can access any property
    - Owners can only access their own properties
    - Tenants can only access properties they're renting
    - Maintenance staff can only access properties assigned to them
    """
    property_repo = PropertyRepositorySupabase()
    property_obj = await property_repo.get_by_id(property_id)
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user has permission to access this property
    if current_user.get("role") != "admin" and (
        (current_user.get("role") == "owner" and str(property_obj.get("owner_id")) != str(current_user.get("user_id")))
        # TODO: Add proper checks for tenant and maintenance roles
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this property"
        )
        
    return property_obj

@router.patch("/{property_id}", response_model=Dict[str, Any])
async def update_property(
    property_id: UUID,
    property_in: PropertyUpdate,
    current_user = Depends(get_current_owner)
):
    """
    Update a property with the provided data.
    - Only owners of the property and admins can update it
    """
    property_repo = PropertyRepositorySupabase()
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.get("role") != "admin" and str(db_property.get("owner_id")) != str(current_user.get("user_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this property"
        )
    
    property_data = property_in.model_dump(exclude_unset=True)
    updated_property = await property_repo.update(property_id, property_data)
    return updated_property

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: UUID,
    current_user = Depends(get_current_owner)
):
    """
    Delete a property (soft delete - marks as deleted).
    - Only owners of the property and admins can delete it
    """
    property_repo = PropertyRepositorySupabase()
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.get("role") != "admin" and str(db_property.get("owner_id")) != str(current_user.get("user_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this property"
        )
    
    await property_repo.delete(property_id)
    return None

@router.post("/{property_id}/images", status_code=status.HTTP_200_OK)
async def upload_property_images(
    property_id: UUID,
    images: List[UploadFile] = File(...),
    current_user = Depends(get_current_owner)
):
    """
    Upload images for a property.
    - Only owners of the property and admins can upload images
    """
    property_repo = PropertyRepositorySupabase()
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.get("role") != "admin" and str(db_property.get("owner_id")) != str(current_user.get("user_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload images for this property"
        )
    
    # TODO: Implement image upload to storage
    # For now, return a placeholder response
    return {
        "property_id": str(property_id),
        "images": [f"https://storage.example.com/properties/{property_id}_{i+1}.jpg" for i in range(len(images))]
    } 