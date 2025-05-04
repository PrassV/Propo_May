import httpx
import json
from typing import Dict, Any, List, Optional, Union
import asyncio
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with the MCP server for testing purposes."""
    
    def __init__(self, mcp_url: str = "https://propomay-production.up.railway.app/mcp"):
        """
        Initialize the MCP client.
        
        Args:
            mcp_url: URL of the MCP server
        """
        self.mcp_url = mcp_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a SQL query via the MCP server.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            Query results
        """
        payload = {
            "query": query,
            "params": params or {}
        }
        
        try:
            response = await self.client.post(f"{self.mcp_url}/execute_query", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error executing query: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    async def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Insert data into a table via the MCP server.
        
        Args:
            table: Name of the table
            data: Data to insert (single record or list of records)
            
        Returns:
            Insert results
        """
        if not isinstance(data, list):
            data = [data]
            
        payload = {
            "table": table,
            "data": data
        }
        
        try:
            response = await self.client.post(f"{self.mcp_url}/insert_data", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error inserting data: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise
    
    async def update_data(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in a table via the MCP server.
        
        Args:
            table: Name of the table
            data: Data to update
            where: Where condition for the update
            
        Returns:
            Update results
        """
        payload = {
            "table": table,
            "data": data,
            "where": where
        }
        
        try:
            response = await self.client.post(f"{self.mcp_url}/update_data", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating data: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            raise
    
    async def delete_data(self, table: str, where: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete data from a table via the MCP server.
        
        Args:
            table: Name of the table
            where: Where condition for the delete
            
        Returns:
            Delete results
        """
        payload = {
            "table": table,
            "where": where
        }
        
        try:
            response = await self.client.post(f"{self.mcp_url}/delete_data", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting data: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error deleting data: {str(e)}")
            raise
    
    async def describe_schema(self, table: Optional[str] = None) -> Dict[str, Any]:
        """
        Get schema information via the MCP server.
        
        Args:
            table: Optional table name to get schema for
            
        Returns:
            Schema information
        """
        payload = {}
        if table:
            payload["table"] = table
        
        try:
            response = await self.client.post(f"{self.mcp_url}/describe_schema", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting schema: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            raise
            
    # User-specific helper methods
    
    async def create_test_user(self, email: str, password: str, first_name: str = "Test", 
                              last_name: str = "User", role: str = "tenant") -> Dict[str, Any]:
        """
        Create a test user for testing purposes.
        
        This creates both the Supabase Auth user and inserts the metadata.
        
        Args:
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            role: User role
            
        Returns:
            Created user data
        """
        # First, create the user in Supabase Auth table
        # This simulates the Auth API without actually calling it
        auth_user = {
            "email": email,
            "encrypted_password": f"fake_hashed_{password}",
            "email_confirmed_at": "2023-01-01T00:00:00Z",
            "confirmation_sent_at": "2023-01-01T00:00:00Z",
            "confirmation_token": "fake_token",
            "recovery_sent_at": None,
            "recovery_token": None,
            "last_sign_in_at": None,
        }
        
        # Insert the auth user directly into the auth.users table
        auth_result = await self.insert_data("auth.users", auth_user)
        
        # Get the user ID assigned by the database
        user_id = auth_result["data"][0]["id"]
        
        # Now insert the user metadata
        user_metadata = {
            "user_id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "status": "active",
            "password_hash": "SUPABASE_AUTH_MANAGED"
        }
        
        # Insert into our users table
        await self.insert_data("public.users", user_metadata)
        
        return {**user_metadata, "id": user_id}
    
    async def delete_test_user(self, email: str) -> None:
        """
        Delete a test user.
        
        Args:
            email: User email to delete
        """
        # First get the user ID from the users table
        result = await self.execute_query(
            "SELECT user_id FROM public.users WHERE email = :email",
            {"email": email}
        )
        
        if not result["data"]:
            # User doesn't exist
            return
            
        user_id = result["data"][0]["user_id"]
        
        # Delete from users table
        await self.delete_data("public.users", {"email": email})
        
        # Delete from auth.users table
        await self.delete_data("auth.users", {"id": user_id})
        
    async def clean_up_test_users(self, email_pattern: str = "test%") -> None:
        """
        Clean up all test users matching a pattern.
        
        Args:
            email_pattern: SQL LIKE pattern for test emails
        """
        # First get all test user IDs
        result = await self.execute_query(
            "SELECT user_id FROM public.users WHERE email LIKE :pattern",
            {"pattern": email_pattern}
        )
        
        if not result["data"]:
            return
            
        user_ids = [row["user_id"] for row in result["data"]]
        
        # Delete from users table
        await self.execute_query(
            "DELETE FROM public.users WHERE email LIKE :pattern",
            {"pattern": email_pattern}
        )
        
        # Delete from auth.users table
        placeholders = ",".join([f"'{uid}'" for uid in user_ids])
        await self.execute_query(f"DELETE FROM auth.users WHERE id IN ({placeholders})") 