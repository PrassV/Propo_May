from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.unit import Unit, UnitCreate, UnitUpdate, UnitWithDetails, UnitStatus
from app.db.repositories.unit_repository import UnitRepository
from app.db.repositories.property_repository import PropertyRepository
from app.api.dependencies.auth import get_current_active_user, get_current_owner, get_current_admin

router = APIRouter()

@router.post("/properties/{property_id}/units", response_model=Unit, status_code=status.HTTP_201_CREATED)
async def create_unit(
    property_id: UUID,
    unit_in: UnitCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    """
    Create a new unit in a property.
    - Only owners of the property and admins can create units
    """
    # Check if property exists and user has permission
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user is owner of the property or admin
    if current_user.role.value != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create units in this property"
        )
    
    unit_data = unit_in.model_dump(exclude={"unit_images"})
    unit_data["property_id"] = property_id
    
    # TODO: Handle unit_images upload to storage
    
    unit_repo = UnitRepository(db)
    created_unit = await unit_repo.create(unit_data)
    return created_unit

@router.get("/properties/{property_id}/units", response_model=List[Unit])
async def list_units(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[UnitStatus] = None,
    bedrooms: Optional[float] = None,
    min_rent: Optional[float] = None,
    max_rent: Optional[float] = None
):
    """
    List units in a property with optional filtering.
    - Admins can see all units
    - Owners can only see units in their properties
    - Tenants can only see units they're renting or have applied for
    - Maintenance staff can only see units in properties assigned to them
    """
    # Check if property exists
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(property_id)
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check if user has permission to access this property
    if current_user.role.value != "admin" and (
        (current_user.role.value == "owner" and db_property.owner_id != current_user.id)
        # TODO: Add proper checks for tenant and maintenance roles
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access units in this property"
        )
    
    unit_repo = UnitRepository(db)
    units = await unit_repo.list_by_property(
        property_id=property_id,
        skip=skip,
        limit=limit,
        status=status,
        bedrooms=bedrooms,
        min_rent=min_rent,
        max_rent=max_rent
    )
    
    return units

@router.get("/units/{unit_id}", response_model=UnitWithDetails)
async def get_unit(
    unit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific unit.
    - Admins can access any unit
    - Owners can only access units in their properties
    - Tenants can only access units they're renting or have applied for
    - Maintenance staff can only access units in properties assigned to them
    """
    unit_repo = UnitRepository(db)
    unit_with_details = await unit_repo.get_unit_with_details(unit_id)
    
    if not unit_with_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if user has permission to access this unit
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(unit_with_details["property_id"])
    
    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    if current_user.role.value != "admin" and (
        (current_user.role.value == "owner" and db_property.owner_id != current_user.id)
        # TODO: Add proper checks for tenant and maintenance roles
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this unit"
        )
    
    # Add property information to the response
    property_dict = {
        "property_id": str(db_property.id),
        "name": db_property.name,
        "address": {
            "street": db_property.street,
            "city": db_property.city,
            "state": db_property.state,
            "zip": db_property.zip
        }
    }
    unit_with_details["property"] = property_dict
    
    return unit_with_details

@router.patch("/units/{unit_id}", response_model=Unit)
async def update_unit(
    unit_id: UUID,
    unit_in: UnitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    """
    Update a unit with the provided data.
    - Only owners of the property and admins can update units
    """
    unit_repo = UnitRepository(db)
    db_unit = await unit_repo.get_by_id(unit_id)
    
    if not db_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if user is owner of the property or admin
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(db_unit.property_id)
    
    if current_user.role.value != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this unit"
        )
    
    unit_data = unit_in.model_dump(exclude_unset=True)
    updated_unit = await unit_repo.update(unit_id, unit_data)
    return updated_unit

@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    unit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    """
    Delete a unit (soft delete - marks as inactive).
    - Only owners of the property and admins can delete units
    """
    unit_repo = UnitRepository(db)
    db_unit = await unit_repo.get_by_id(unit_id)
    
    if not db_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if user is owner of the property or admin
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(db_unit.property_id)
    
    if current_user.role.value != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this unit"
        )
    
    await unit_repo.delete(unit_id)
    return None

@router.post("/units/{unit_id}/images", status_code=status.HTTP_200_OK)
async def upload_unit_images(
    unit_id: UUID,
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_owner)
):
    """
    Upload images for a unit.
    - Only owners of the property and admins can upload images
    """
    unit_repo = UnitRepository(db)
    db_unit = await unit_repo.get_by_id(unit_id)
    
    if not db_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if user is owner of the property or admin
    property_repo = PropertyRepository(db)
    db_property = await property_repo.get_by_id(db_unit.property_id)
    
    if current_user.role.value != "admin" and db_property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload images for this unit"
        )
    
    # TODO: Implement image upload to storage
    # For now, return a placeholder response
    return {
        "unit_id": str(unit_id),
        "images": [f"https://storage.example.com/units/{unit_id}_{i+1}.jpg" for i in range(len(images))]
    } 