from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.unit import Unit, UnitStatus

class UnitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, unit_data: dict) -> Unit:
        db_unit = Unit(**unit_data)
        self.db.add(db_unit)
        await self.db.commit()
        await self.db.refresh(db_unit)
        return db_unit
    
    async def get_by_id(self, unit_id: UUID) -> Optional[Unit]:
        result = await self.db.execute(select(Unit).where(Unit.id == unit_id))
        return result.scalars().first()
    
    async def list_by_property(self, 
                             property_id: UUID,
                             skip: int = 0, 
                             limit: int = 100,
                             status: Optional[UnitStatus] = None,
                             bedrooms: Optional[float] = None,
                             min_rent: Optional[float] = None,
                             max_rent: Optional[float] = None) -> List[Unit]:
        query = select(Unit).where(Unit.property_id == property_id)
        
        if status:
            query = query.where(Unit.status == status)
        
        if bedrooms:
            query = query.where(Unit.bedrooms == bedrooms)
        
        if min_rent:
            query = query.where(Unit.rent_amount >= min_rent)
            
        if max_rent:
            query = query.where(Unit.rent_amount <= max_rent)
            
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[Unit]:
        # This will need to be updated when we have the Lease model
        # For now, returning an empty list
        return []
    
    async def update(self, unit_id: UUID, unit_data: dict) -> Optional[Unit]:
        await self.db.execute(
            update(Unit).where(Unit.id == unit_id).values(**unit_data)
        )
        await self.db.commit()
        return await self.get_by_id(unit_id)
    
    async def delete(self, unit_id: UUID) -> None:
        # Soft delete - update status to inactive
        await self.update(unit_id, {"status": UnitStatus.inactive})
    
    async def hard_delete(self, unit_id: UUID) -> None:
        # Hard delete - remove from database
        await self.db.execute(delete(Unit).where(Unit.id == unit_id))
        await self.db.commit()
        
    async def get_unit_with_details(self, unit_id: UUID) -> Optional[Dict[str, Any]]:
        unit_obj = await self.get_by_id(unit_id)
        if not unit_obj:
            return None
            
        # Convert SQLAlchemy object to dict
        unit_dict = {
            "unit_id": unit_obj.id,
            "property_id": unit_obj.property_id,
            "unit_number": unit_obj.unit_number,
            "floor": unit_obj.floor,
            "bedrooms": float(unit_obj.bedrooms),
            "bathrooms": float(unit_obj.bathrooms),
            "square_feet": unit_obj.square_feet,
            "rent_amount": float(unit_obj.rent_amount),
            "security_deposit": float(unit_obj.security_deposit),
            "status": unit_obj.status.value,
            "amenities": unit_obj.amenities,
            "description": unit_obj.description,
            "created_at": unit_obj.created_at,
            "updated_at": unit_obj.updated_at,
            "images": [],  # Placeholder for unit images
            "property": None,  # Placeholder for property details
            "tenant": None,  # Placeholder for tenant details
            "lease": None  # Placeholder for lease details
        }
        
        return unit_dict 