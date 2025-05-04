import asyncio
import pytest
import uuid
import httpx
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime, timedelta
import json
import logging
from tests.mcp_client import MCPClient

logger = logging.getLogger(__name__)

class AuthTestBase:
    """Base class for authentication and user-related tests."""
    
    # API endpoint base URL
    BASE_URL = "https://propomay-production.up.railway.app"
    API_PREFIX = "/api"
    
    # Test user data
    TEST_USER_EMAIL_PREFIX = "test_user_"
    TEST_USER_PASSWORD = "Test@123456"
    
    @pytest.fixture(scope="class")
    async def mcp_client(self) -> AsyncGenerator[MCPClient, None]:
        """Fixture to provide an MCP client for database access."""
        client = MCPClient()
        yield client
        await client.close()
    
    @pytest.fixture(scope="class")
    async def api_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Fixture to provide an HTTP client for API testing."""
        async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0) as client:
            yield client
    
    @pytest.fixture(scope="function")
    async def test_user(self, mcp_client: MCPClient) -> Dict[str, Any]:
        """
        Fixture to create a test user for a test and clean it up afterwards.
        
        Returns:
            Dict containing the test user data
        """
        # Generate a unique email for this test
        unique_id = uuid.uuid4().hex[:8]
        email = f"{self.TEST_USER_EMAIL_PREFIX}{unique_id}@example.com"
        
        # Create the test user
        user = await mcp_client.create_test_user(
            email=email,
            password=self.TEST_USER_PASSWORD,
            first_name="Test",
            last_name="User",
            role="tenant"
        )
        
        yield user
        
        # Clean up the test user
        await mcp_client.delete_test_user(email)
    
    @pytest.fixture(scope="function")
    async def test_admin_user(self, mcp_client: MCPClient) -> Dict[str, Any]:
        """
        Fixture to create a test admin user for a test and clean it up afterwards.
        
        Returns:
            Dict containing the test admin user data
        """
        # Generate a unique email for this test
        unique_id = uuid.uuid4().hex[:8]
        email = f"{self.TEST_USER_EMAIL_PREFIX}admin_{unique_id}@example.com"
        
        # Create the test admin user
        user = await mcp_client.create_test_user(
            email=email,
            password=self.TEST_USER_PASSWORD,
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        
        yield user
        
        # Clean up the test user
        await mcp_client.delete_test_user(email)
    
    @pytest.fixture(scope="function")
    async def test_owner_user(self, mcp_client: MCPClient) -> Dict[str, Any]:
        """
        Fixture to create a test property owner user for a test and clean it up afterwards.
        
        Returns:
            Dict containing the test owner user data
        """
        # Generate a unique email for this test
        unique_id = uuid.uuid4().hex[:8]
        email = f"{self.TEST_USER_EMAIL_PREFIX}owner_{unique_id}@example.com"
        
        # Create the test owner user
        user = await mcp_client.create_test_user(
            email=email,
            password=self.TEST_USER_PASSWORD,
            first_name="Owner",
            last_name="User",
            role="owner"
        )
        
        yield user
        
        # Clean up the test user
        await mcp_client.delete_test_user(email)
    
    @pytest.fixture(scope="function")
    async def test_maintenance_user(self, mcp_client: MCPClient) -> Dict[str, Any]:
        """
        Fixture to create a test maintenance user for a test and clean it up afterwards.
        
        Returns:
            Dict containing the test maintenance user data
        """
        # Generate a unique email for this test
        unique_id = uuid.uuid4().hex[:8]
        email = f"{self.TEST_USER_EMAIL_PREFIX}maint_{unique_id}@example.com"
        
        # Create the test maintenance user
        user = await mcp_client.create_test_user(
            email=email,
            password=self.TEST_USER_PASSWORD,
            first_name="Maintenance",
            last_name="User",
            role="maintenance"
        )
        
        yield user
        
        # Clean up the test user
        await mcp_client.delete_test_user(email)
    
    @pytest.fixture(scope="function")
    async def user_token(self, api_client: httpx.AsyncClient, test_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fixture to log in a test user and get their auth token.
        
        Returns:
            Dict containing token information
        """
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_user["email"],
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data["token_type"],
            "auth_header": f"{token_data['token_type']} {token_data['access_token']}"
        }
    
    @pytest.fixture(scope="function")
    async def admin_token(self, api_client: httpx.AsyncClient, test_admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fixture to log in a test admin user and get their auth token.
        
        Returns:
            Dict containing token information
        """
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_admin_user["email"],
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data["token_type"],
            "auth_header": f"{token_data['token_type']} {token_data['access_token']}"
        }
    
    @classmethod
    async def verify_user_in_db(cls, mcp_client: MCPClient, email: str) -> bool:
        """
        Verify that a user exists in the database.
        
        Args:
            mcp_client: MCP client
            email: User email to check
            
        Returns:
            True if the user exists, False otherwise
        """
        result = await mcp_client.execute_query(
            "SELECT * FROM public.users WHERE email = :email",
            {"email": email}
        )
        
        return len(result["data"]) > 0
    
    @classmethod
    async def verify_user_in_auth(cls, mcp_client: MCPClient, email: str) -> bool:
        """
        Verify that a user exists in the Supabase Auth table.
        
        Args:
            mcp_client: MCP client
            email: User email to check
            
        Returns:
            True if the user exists, False otherwise
        """
        result = await mcp_client.execute_query(
            "SELECT * FROM auth.users WHERE email = :email",
            {"email": email}
        )
        
        return len(result["data"]) > 0
    
    @classmethod
    def generate_test_email(cls) -> str:
        """
        Generate a unique test email.
        
        Returns:
            Unique test email
        """
        unique_id = uuid.uuid4().hex[:8]
        return f"{cls.TEST_USER_EMAIL_PREFIX}{unique_id}@example.com"
        
    @pytest.fixture(autouse=True)
    async def cleanup_test_users(self, mcp_client: MCPClient):
        """Fixture to clean up any test users that might have been left behind."""
        yield
        # After each test, clean up any test users
        await mcp_client.clean_up_test_users(f"{self.TEST_USER_EMAIL_PREFIX}%") 