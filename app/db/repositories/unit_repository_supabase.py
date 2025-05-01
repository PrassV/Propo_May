from typing import Optional, List, Dict, Any
from uuid import UUID
from app.db.supabase import supabase
from app.db.supabase_db import SupabaseTable
from app.models.unit import UnitStatus
import logging

logger = logging.getLogger(__name__)

class UnitRepositorySupabase:
    def __init__(self):
        # No need to specify pk_column, SupabaseTable will use the correct one from the mapping
        self.table = SupabaseTable("units")
    
    async def create(self, unit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new unit in the database."""
        try:
            # Convert enum to string if present
            if "status" in unit_data and isinstance(unit_data["status"], UnitStatus):
                unit_data["status"] = unit_data["status"].value
            
            # Handle amenities array
            if "amenities" in unit_data and unit_data["amenities"] is None:
                unit_data["amenities"] = []
                
            return await self.table.create(unit_data)
            
        except Exception as e:
            logger.error(f"Error creating unit: {e}")
            raise
    
    async def get_by_id(self, unit_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a unit by ID"""
        try:
            return await self.table.get_by_id(str(unit_id))
        except Exception as e:
            logger.error(f"Error getting unit by ID: {e}")
            raise
    
    async def list_by_property(self, 
                             property_id: UUID,
                             skip: int = 0, 
                             limit: int = 100,
                             status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List units for a specific property with optional filtering"""
        try:
            # Build filters
            filters = {"property_id": str(property_id)}
            
            if status:
                if isinstance(status, UnitStatus):
                    filters["status"] = status.value
                else:
                    filters["status"] = status
                
            return await self.table.list(filters=filters, offset=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error listing units by property: {e}")
            raise
    
    async def list(self, 
                 skip: int = 0, 
                 limit: int = 100,
                 status: Optional[str] = None,
                 min_rent: Optional[float] = None,
                 max_rent: Optional[float] = None,
                 bedrooms: Optional[float] = None,
                 bathrooms: Optional[float] = None) -> List[Dict[str, Any]]:
        """List units with optional filtering"""
        try:
            # Build initial filters
            filters = {}
            
            if status:
                if isinstance(status, UnitStatus):
                    filters["status"] = status.value
                else:
                    filters["status"] = status
                
            # Execute base query with simple filters
            units = await self.table.list(filters=filters, offset=skip, limit=limit)
            
            # Apply additional filters (these require post-processing)
            if min_rent is not None:
                units = [u for u in units if float(u.get("rent_amount", 0)) >= min_rent]
                
            if max_rent is not None:
                units = [u for u in units if float(u.get("rent_amount", 0)) <= max_rent]
                
            if bedrooms is not None:
                units = [u for u in units if float(u.get("bedrooms", 0)) == bedrooms]
                
            if bathrooms is not None:
                units = [u for u in units if float(u.get("bathrooms", 0)) == bathrooms]
                
            return units
        except Exception as e:
            logger.error(f"Error listing units: {e}")
            raise
    
    async def update(self, unit_id: UUID, unit_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a unit"""
        try:
            # Convert enum to string if present
            if "status" in unit_data and isinstance(unit_data["status"], UnitStatus):
                unit_data["status"] = unit_data["status"].value
                
            return await self.table.update(str(unit_id), unit_data)
        except Exception as e:
            logger.error(f"Error updating unit: {e}")
            raise
    
    async def delete(self, unit_id: UUID) -> bool:
        """Delete a unit (mark as inactive)"""
        try:
            # Instead of deleting, we set status to inactive
            return bool(await self.table.update(str(unit_id), {"status": UnitStatus.inactive.value}))
        except Exception as e:
            logger.error(f"Error updating unit status: {e}")
            raise 