from typing import Optional, List, Dict, Any
from uuid import UUID
from app.db.supabase import supabase
from app.db.supabase_db import SupabaseTable
from app.models.property import PropertyStatus
import logging

logger = logging.getLogger(__name__)

class PropertyRepositorySupabase:
    def __init__(self):
        # No need to specify pk_column, SupabaseTable will use the correct one from the mapping
        self.table = SupabaseTable("properties")
    
    async def create(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new property in the database."""
        try:
            # Convert enum to string if present
            if "status" in property_data and isinstance(property_data["status"], PropertyStatus):
                property_data["status"] = property_data["status"].value
            
            # Handle amenities array
            if "amenities" in property_data and property_data["amenities"] is None:
                property_data["amenities"] = []
                
            return await self.table.create(property_data)
            
        except Exception as e:
            logger.error(f"Error creating property: {e}")
            raise
    
    async def get_by_id(self, property_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a property by ID"""
        try:
            return await self.table.get_by_id(str(property_id))
        except Exception as e:
            logger.error(f"Error getting property by ID: {e}")
            raise
    
    async def list(self, 
                  owner_id: Optional[UUID] = None, 
                  skip: int = 0, 
                  limit: int = 100,
                  city: Optional[str] = None,
                  state: Optional[str] = None,
                  property_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List properties with optional filtering"""
        try:
            # Build filters
            filters = {}
            if owner_id:
                filters["owner_id"] = str(owner_id)
                
            # Execute base query with filters
            properties = await self.table.list(filters=filters, offset=skip, limit=limit)
            
            # Apply additional filters (these aren't supported by simple eq filtering)
            if city:
                properties = [p for p in properties if city.lower() in p.get("city", "").lower()]
            
            if state:
                properties = [p for p in properties if p.get("state") == state]
                
            if property_type:
                properties = [p for p in properties if p.get("property_type") == property_type]
                
            return properties
        except Exception as e:
            logger.error(f"Error listing properties: {e}")
            raise
    
    async def update(self, property_id: UUID, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a property"""
        try:
            # Convert enum to string if present
            if "status" in property_data and isinstance(property_data["status"], PropertyStatus):
                property_data["status"] = property_data["status"].value
                
            return await self.table.update(str(property_id), property_data)
        except Exception as e:
            logger.error(f"Error updating property: {e}")
            raise
    
    async def delete(self, property_id: UUID) -> bool:
        """Delete a property (mark as deleted)"""
        try:
            # Instead of deleting, we set status to deleted
            return bool(await self.table.update(str(property_id), {"status": PropertyStatus.deleted.value}))
        except Exception as e:
            logger.error(f"Error updating property status: {e}")
            raise 