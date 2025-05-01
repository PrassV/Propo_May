from typing import Optional, List, Dict, Any
from uuid import UUID
from app.db.supabase import supabase
from app.db.supabase_db import SupabaseTable
from app.models.user import UserRole, UserStatus
import logging

logger = logging.getLogger(__name__)

class UserRepositorySupabase:
    def __init__(self):
        # No need to specify pk_column, SupabaseTable will use the correct one from the mapping
        self.table = SupabaseTable("users")
    
    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in the database.
        Authentication is handled by Supabase Auth, this just stores additional user data.
        """
        try:
            # No need to handle password, as Supabase Auth takes care of it
            if "password" in user_data:
                del user_data["password"]
            
            # Ensure we have the correct field names according to Supabase
            if "role" in user_data and isinstance(user_data["role"], UserRole):
                user_data["role"] = user_data["role"].value
                
            if "status" in user_data and isinstance(user_data["status"], UserStatus):
                user_data["status"] = user_data["status"].value
            
            return await self.table.create(user_data)
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        try:
            return await self.table.get_by_id(str(user_id))
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email"""
        try:
            return await self.table.get_by_field("email", email)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise
    
    async def get_by_supabase_uid(self, supabase_uid: str) -> Optional[Dict[str, Any]]:
        """Get a user by Supabase Auth ID"""
        try:
            results = await self.table.get_by_field("supabase_uid", supabase_uid)
            if results:
                return results[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by Supabase UID: {str(e)}")
            raise
    
    async def list(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """List users with optional filtering by role"""
        try:
            filters = {}
            if role:
                filters["role"] = role
                
            return await self.table.list(filters=filters, offset=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise
    
    async def update(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a user"""
        try:
            # No need to handle password, as Supabase Auth takes care of it
            if "password" in user_data:
                del user_data["password"]
                
            # Ensure we have the correct field names according to Supabase
            if "role" in user_data and isinstance(user_data["role"], UserRole):
                user_data["role"] = user_data["role"].value
                
            if "status" in user_data and isinstance(user_data["status"], UserStatus):
                user_data["status"] = user_data["status"].value
                
            return await self.table.update(str(user_id), user_data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user (mark as inactive)"""
        try:
            # Instead of deleting, we set status to inactive
            return bool(await self.table.update(str(user_id), {"status": UserStatus.inactive.value}))
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            raise 