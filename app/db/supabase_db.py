from app.db.supabase import supabase
from typing import Dict, List, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class SupabaseTable:
    """Base class for interacting with Supabase tables"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the table"""
        try:
            # Add automatic UUID if id not provided
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
                
            response = supabase.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]
            return {}
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {str(e)}")
            raise
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        try:
            response = supabase.table(self.table_name).select("*").eq("id", id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting record from {self.table_name}: {str(e)}")
            raise
    
    async def get_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Get records by field value"""
        try:
            response = supabase.table(self.table_name).select("*").eq(field, value).execute()
            
            if response.data:
                return response.data
            return []
        except Exception as e:
            logger.error(f"Error getting records from {self.table_name} by {field}: {str(e)}")
            raise
    
    async def list(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """List records with optional filters"""
        try:
            query = supabase.table(self.table_name).select("*")
            
            # Apply any filters
            for field, value in filters.items():
                if value is not None:
                    if field.startswith('ilike_'):
                        actual_field = field[6:]  # Remove 'ilike_' prefix
                        query = query.ilike(actual_field, f"%{value}%")
                    else:
                        query = query.eq(field, value)
            
            # Apply pagination
            query = query.range(skip, skip + limit - 1)
            
            response = query.execute()
            
            if response.data:
                return response.data
            return []
        except Exception as e:
            logger.error(f"Error listing records from {self.table_name}: {str(e)}")
            raise
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID"""
        try:
            response = supabase.table(self.table_name).update(data).eq("id", id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {str(e)}")
            raise
    
    async def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        try:
            response = supabase.table(self.table_name).delete().eq("id", id).execute()
            
            if response.data and len(response.data) > 0:
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting record from {self.table_name}: {str(e)}")
            raise
    
    async def execute_rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """Execute a stored procedure"""
        try:
            response = supabase.rpc(function_name, params).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error executing RPC {function_name}: {str(e)}")
            raise 