from app.db.supabase import supabase
from typing import Dict, List, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

# Primary key mapping based on MCP schema info
TABLE_PRIMARY_KEY_MAP = {
    "users": "user_id",
    "properties": "property_id",
    "units": "unit_id",
    "tasks": "task_id",
    "documents": "document_id",
    "inspections": "inspection_id",
    "maintenance_requests": "request_id",
    "invoices": "invoice_id",
    "payments": "payment_id",
    "leases": "lease_id",
    "reports": "report_id",
    "unit_listings": "listing_id"
}

class SupabaseTable:
    """Base class for interacting with Supabase tables"""
    
    def __init__(self, table_name: str, pk_column: Optional[str] = None):
        self.table_name = table_name
        # Use provided pk_column or look it up in the mapping, falling back to "id"
        self.pk_column = pk_column or TABLE_PRIMARY_KEY_MAP.get(table_name, "id")
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the table"""
        try:
            # Add automatic UUID if primary key not provided
            if self.pk_column not in data:
                data[self.pk_column] = str(uuid.uuid4())
                
            response = supabase.table(self.table_name).insert(data).execute()
            
            if response.data:
                return response.data[0]
            else:
                logger.error(f"Create failed for {self.table_name}: {response.error}")
                return {}
                
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            raise
    
    async def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record by its primary key"""
        try:
            response = supabase.table(self.table_name).select("*").eq(self.pk_column, record_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
                
        except Exception as e:
            logger.error(f"Error getting record by ID from {self.table_name}: {e}")
            raise
    
    async def get_by_field(self, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get a record by a specific field value"""
        try:
            response = supabase.table(self.table_name).select("*").eq(field, value).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
                
        except Exception as e:
            logger.error(f"Error getting record by field from {self.table_name}: {e}")
            raise
    
    async def list(self, filters: Optional[Dict[str, Any]] = None, 
                  limit: Optional[int] = None, 
                  offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List records with optional filters, limit and offset"""
        try:
            query = supabase.table(self.table_name).select("*")
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
                    
            # Apply limit and offset if provided
            if limit is not None:
                query = query.limit(limit)
                
            if offset is not None:
                query = query.offset(offset)
                
            response = query.execute()
            
            if response.data:
                return response.data
            return []
                
        except Exception as e:
            logger.error(f"Error listing records from {self.table_name}: {e}")
            raise
            
    async def update(self, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by its primary key"""
        try:
            response = supabase.table(self.table_name).update(data).eq(self.pk_column, record_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
                
        except Exception as e:
            logger.error(f"Error updating record in {self.table_name}: {e}")
            raise
            
    async def delete(self, record_id: str) -> bool:
        """Delete a record by its primary key"""
        try:
            response = supabase.table(self.table_name).delete().eq(self.pk_column, record_id).execute()
            
            if response.data:
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error deleting record from {self.table_name}: {e}")
            raise
    
    async def execute_rpc(self, function_name: str, params: Dict[str, Any]) -> Any:
        """Execute a stored procedure"""
        try:
            response = supabase.rpc(function_name, params).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error executing RPC {function_name}: {str(e)}")
            raise 