from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, case
from app.models.property import Property, PropertyStatus
from app.models.unit import Unit, UnitStatus

class PropertyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, property_data: dict) -> Property:
        db_property = Property(**property_data)
        self.db.add(db_property)
        await self.db.commit()
        await self.db.refresh(db_property)
        return db_property
    
    async def get_by_id(self, property_id: UUID) -> Optional[Property]:
        result = await self.db.execute(select(Property).where(Property.property_id == property_id))
        return result.scalars().first()
    
    async def list(self, 
                  owner_id: Optional[UUID] = None, 
                  skip: int = 0, 
                  limit: int = 100,
                  city: Optional[str] = None,
                  state: Optional[str] = None,
                  property_type: Optional[str] = None) -> List[Property]:
        query = select(Property).where(Property.status != PropertyStatus.deleted)
        
        if owner_id:
            query = query.where(Property.owner_id == owner_id)
        
        if city:
            query = query.where(Property.city.ilike(f"%{city}%"))
        
        if state:
            query = query.where(Property.state == state)
            
        if property_type:
            query = query.where(Property.property_type == property_type)
            
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, property_id: UUID, property_data: dict) -> Optional[Property]:
        await self.db.execute(
            update(Property).where(Property.property_id == property_id).values(**property_data)
        )
        await self.db.commit()
        return await self.get_by_id(property_id)
    
    async def delete(self, property_id: UUID) -> None:
        # Soft delete - update status to deleted
        await self.update(property_id, {"status": PropertyStatus.deleted})
    
    async def hard_delete(self, property_id: UUID) -> None:
        # Hard delete - remove from database
        await self.db.execute(delete(Property).where(Property.property_id == property_id))
        await self.db.commit()
        
    async def get_with_unit_stats(self, property_id: UUID) -> Optional[Dict[str, Any]]:
        property_obj = await self.get_by_id(property_id)
        if not property_obj:
            return None
            
        # Get unit statistics
        result = await self.db.execute(
            select(
                func.count(Unit.unit_id).label("total_units"),
                func.sum(case([(Unit.status == UnitStatus.available, 1)], else_=0)).label("available_units"),
                func.sum(case([(Unit.status == UnitStatus.occupied, 1)], else_=0)).label("occupied_units")
            ).where(Unit.property_id == property_id)
        )
        
        stats = result.first()
        
        # Convert SQLAlchemy object to dict
        property_dict = {
            "property_id": property_obj.property_id,
            "owner_id": property_obj.owner_id,
            "name": property_obj.name,
            "street": property_obj.street,
            "city": property_obj.city,
            "state": property_obj.state,
            "zip": property_obj.zip,
            "country": property_obj.country,
            "latitude": property_obj.latitude,
            "longitude": property_obj.longitude,
            "property_type": property_obj.property_type,
            "year_built": property_obj.year_built,
            "total_units": property_obj.total_units,
            "amenities": property_obj.amenities,
            "description": property_obj.description,
            "status": property_obj.status.value,
            "tax_id": property_obj.tax_id,
            "created_at": property_obj.created_at,
            "updated_at": property_obj.updated_at,
            "available_units": stats.available_units if stats.available_units else 0,
            "occupied_units": stats.occupied_units if stats.occupied_units else 0,
            "images": []  # Placeholder for property images
        }
        
        return property_dict 