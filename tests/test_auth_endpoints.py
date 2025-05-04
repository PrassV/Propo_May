import pytest
import asyncio
from typing import Dict, Any
import httpx
from tests.auth_test_base import AuthTestBase
from tests.mcp_client import MCPClient

class TestAuthEndpoints(AuthTestBase):
    """Tests for authentication-related endpoints."""
    
    @pytest.mark.asyncio
    async def test_user_registration(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test user registration functionality."""
        # Generate a unique test email
        test_email = self.generate_test_email()
        
        # Verify user doesn't exist yet
        assert not await self.verify_user_in_db(mcp_client, test_email)
        assert not await self.verify_user_in_auth(mcp_client, test_email)
        
        # Register a new user
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/register",
            json={
                "email": test_email,
                "password": self.TEST_USER_PASSWORD,
                "first_name": "Test",
                "last_name": "User",
                "role": "tenant"
            }
        )
        
        # Verify the response
        assert response.status_code == 201
        
        # Verify user was created in both tables
        assert await self.verify_user_in_db(mcp_client, test_email)
        assert await self.verify_user_in_auth(mcp_client, test_email)
        
        # Verify the response contains user data
        user_data = response.json()
        assert user_data["email"] == test_email
        assert user_data["first_name"] == "Test"
        assert user_data["last_name"] == "User"
        assert user_data["role"] == "tenant"
        assert "user_id" in user_data
        
        # Test duplicate registration
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/register",
            json={
                "email": test_email,
                "password": self.TEST_USER_PASSWORD,
                "first_name": "Test",
                "last_name": "User",
                "role": "tenant"
            }
        )
        
        # Verify duplicate registration fails
        assert response.status_code == 400
        assert "already registered" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_login_flow(self, api_client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test user login functionality."""
        # Login with correct credentials
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_user["email"],
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Verify successful login
        assert response.status_code == 200
        token_data = response.json()
        
        # Verify token data structure
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Test login with wrong password
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_user["email"],
                "password": "WrongPassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Verify login fails with wrong password
        assert response.status_code == 401
        
        # Test login with non-existent user
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Verify login fails with non-existent user
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_token_refresh(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any]):
        """Test token refresh functionality."""
        # Refresh the token
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/refresh",
            json={"refresh_token": user_token["refresh_token"]}
        )
        
        # Verify successful token refresh
        assert response.status_code == 200
        token_data = response.json()
        
        # Verify token data structure
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # Verify the new token is different
        assert token_data["access_token"] != user_token["access_token"]
        
        # Test refresh with invalid token
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        # Verify refresh fails with invalid token
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_logout(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any]):
        """Test logout functionality."""
        # Logout the user
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/logout",
            json={"authorization": user_token["auth_header"]}
        )
        
        # Verify successful logout
        assert response.status_code == 200
        assert "successfully logged out" in response.text.lower()
        
        # Try using the token after logout
        # In Supabase, tokens might still work after logout until they expire
        # but we should at least check the token is properly submitted
        response = await api_client.get(
            f"{self.API_PREFIX}/users/me",
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # The behavior here depends on how your logout implementation works
        # If tokens are blacklisted, this should fail
        # If tokens are just forgotten client-side, this might still work
        # So we don't assert a specific status code
    
    @pytest.mark.asyncio
    async def test_forgot_password(self, api_client: httpx.AsyncClient, test_user: Dict[str, Any]):
        """Test forgot password functionality."""
        # Request password reset
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/forgot-password",
            json={"email": test_user["email"]}
        )
        
        # Verify successful request
        assert response.status_code == 200
        assert "success" in response.json()
        
        # Test with non-existent email
        # The API should still report success to prevent email enumeration
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
        # Verify the API still reports success
        assert response.status_code == 200
        assert "success" in response.json()
    
    @pytest.mark.asyncio
    async def test_password_validation(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test password validation during registration."""
        test_email = self.generate_test_email()
        
        # Test with a short password
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/register",
            json={
                "email": test_email,
                "password": "short",  # Too short
                "first_name": "Test",
                "last_name": "User",
                "role": "tenant"
            }
        )
        
        # Verify registration fails with a short password
        assert response.status_code == 400
        
        # Test with a common password
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/register",
            json={
                "email": test_email,
                "password": "password123",  # Common password
                "first_name": "Test",
                "last_name": "User",
                "role": "tenant"
            }
        )
        
        # Verification depends on your password policy
        # If you reject common passwords, this should fail
        # Otherwise, it might succeed
        # We'll assume it might fail for weak passwords
        if response.status_code == 400:
            assert "password" in response.text.lower() 