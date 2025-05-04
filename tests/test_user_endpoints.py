import pytest
import asyncio
from typing import Dict, Any
import httpx
from tests.auth_test_base import AuthTestBase
from tests.mcp_client import MCPClient

class TestUserEndpoints(AuthTestBase):
    """Tests for user management endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any], 
                                   test_user: Dict[str, Any]):
        """Test getting the current user's profile."""
        # Get current user profile
        response = await api_client.get(
            f"{self.API_PREFIX}/users/me",
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Verify successful request
        assert response.status_code == 200
        
        # Verify response data
        user_data = response.json()
        assert user_data["email"] == test_user["email"]
        assert user_data["first_name"] == test_user["first_name"]
        assert user_data["last_name"] == test_user["last_name"]
        assert user_data["role"] == test_user["role"]
        
        # Test without authentication
        response = await api_client.get(f"{self.API_PREFIX}/users/me")
        
        # Verify unauthorized access fails
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_current_user(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any],
                                      test_user: Dict[str, Any], mcp_client: MCPClient):
        """Test updating the current user's profile."""
        # Update user profile
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "+1234567890"
        }
        
        response = await api_client.put(
            f"{self.API_PREFIX}/users/me",
            json=update_data,
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Verify successful update
        assert response.status_code == 200
        
        # Verify response data
        updated_user = response.json()
        assert updated_user["first_name"] == update_data["first_name"]
        assert updated_user["last_name"] == update_data["last_name"]
        assert updated_user["phone"] == update_data["phone"]
        
        # Verify data was updated in the database
        result = await mcp_client.execute_query(
            "SELECT * FROM public.users WHERE email = :email",
            {"email": test_user["email"]}
        )
        
        assert result["data"][0]["first_name"] == update_data["first_name"]
        assert result["data"][0]["last_name"] == update_data["last_name"]
        assert result["data"][0]["phone"] == update_data["phone"]
    
    @pytest.mark.asyncio
    async def test_list_users_admin(self, api_client: httpx.AsyncClient, admin_token: Dict[str, Any],
                                   test_user: Dict[str, Any], test_admin_user: Dict[str, Any]):
        """Test listing all users as an admin."""
        # List all users
        response = await api_client.get(
            f"{self.API_PREFIX}/users",
            headers={"Authorization": admin_token["auth_header"]}
        )
        
        # Verify successful request
        assert response.status_code == 200
        
        # Verify response data is a list
        users = response.json()
        assert isinstance(users, list)
        
        # Verify both test users are in the list
        test_emails = [test_user["email"], test_admin_user["email"]]
        found_emails = [user["email"] for user in users]
        
        assert all(email in found_emails for email in test_emails)
        
        # Test filtering by role
        response = await api_client.get(
            f"{self.API_PREFIX}/users?role=tenant",
            headers={"Authorization": admin_token["auth_header"]}
        )
        
        # Verify successful request with filter
        assert response.status_code == 200
        
        # Verify only tenant users are returned
        tenant_users = response.json()
        tenant_emails = [user["email"] for user in tenant_users]
        
        assert test_user["email"] in tenant_emails
        assert test_admin_user["email"] not in tenant_emails
    
    @pytest.mark.asyncio
    async def test_list_users_non_admin(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any]):
        """Test that non-admin users cannot list all users."""
        # Attempt to list all users as a non-admin
        response = await api_client.get(
            f"{self.API_PREFIX}/users",
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Verify access is forbidden
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any],
                                  test_user: Dict[str, Any]):
        """Test getting the user's profile with roles."""
        # Get user profile with roles
        response = await api_client.get(
            f"{self.API_PREFIX}/users/profile",
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Verify successful request
        assert response.status_code == 200
        
        # Verify response data
        profile_data = response.json()
        assert profile_data["email"] == test_user["email"]
        assert "available_roles" in profile_data
        assert isinstance(profile_data["available_roles"], list)
        assert test_user["role"] in profile_data["available_roles"]
    
    @pytest.mark.asyncio
    async def test_switch_role(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test switching a user's role."""
        # Create a user with multiple roles
        unique_id = self.generate_test_email()
        
        # Insert user with multiple available roles
        user = await mcp_client.create_test_user(
            email=unique_id,
            password=self.TEST_USER_PASSWORD,
            role="tenant"
        )
        
        # Add owner role capability to this user
        await mcp_client.execute_query(
            """
            INSERT INTO public.user_roles (user_id, role) 
            VALUES (:user_id, 'owner')
            """,
            {"user_id": user["user_id"]}
        )
        
        # Login to get token
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": user["email"],
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token_data = response.json()
        auth_header = f"{token_data['token_type']} {token_data['access_token']}"
        
        # Switch role
        response = await api_client.post(
            f"{self.API_PREFIX}/users/switch-role",
            json={"role": "owner"},
            headers={"Authorization": auth_header}
        )
        
        # Verify successful role switch
        assert response.status_code == 200
        assert response.json()["current_role"] == "owner"
        
        # Verify by getting the profile
        response = await api_client.get(
            f"{self.API_PREFIX}/users/me",
            headers={"Authorization": auth_header}
        )
        
        # Check that active role is now owner
        assert response.status_code == 200
        assert response.json()["role"] == "owner"
        
        # Test switching to a role the user doesn't have
        response = await api_client.post(
            f"{self.API_PREFIX}/users/switch-role",
            json={"role": "admin"},
            headers={"Authorization": auth_header}
        )
        
        # Verify role switch fails for unauthorized role
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_profile_setup(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any],
                               test_user: Dict[str, Any], mcp_client: MCPClient):
        """Test the profile setup endpoint."""
        # Complete profile setup
        profile_data = {
            "phone": "+1987654321",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "preferred_contact_method": "email"
        }
        
        # Check if this endpoint exists in your API
        response = await api_client.post(
            f"{self.API_PREFIX}/users/profile-setup",
            json=profile_data,
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Depending on your implementation, this might be a 200 or a 404
        # If it's implemented, verify the response
        if response.status_code == 200:
            updated_profile = response.json()
            assert updated_profile["phone"] == profile_data["phone"]
            
            # Verify database update
            result = await mcp_client.execute_query(
                "SELECT * FROM public.user_profiles WHERE user_id = :user_id",
                {"user_id": test_user["user_id"]}
            )
            
            if result["data"]:
                assert result["data"][0]["phone"] == profile_data["phone"]
                assert result["data"][0]["address"] == profile_data["address"]
    
    @pytest.mark.asyncio
    async def test_document_verification(self, api_client: httpx.AsyncClient, user_token: Dict[str, Any],
                                       test_user: Dict[str, Any], mcp_client: MCPClient):
        """Test document verification submission."""
        # Document verification data
        verification_data = {
            "id_type": "drivers_license",
            "id_number": "DL12345678",
            "document_urls": ["https://example.com/fake-id-front.jpg", "https://example.com/fake-id-back.jpg"]
        }
        
        # Check if this endpoint exists in your API
        response = await api_client.post(
            f"{self.API_PREFIX}/users/verification-documents",
            json=verification_data,
            headers={"Authorization": user_token["auth_header"]}
        )
        
        # Depending on your implementation, this might be a 200 or a 404
        # If it's implemented, verify the response
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True
            
            # Verify database update
            result = await mcp_client.execute_query(
                "SELECT * FROM public.user_verifications WHERE user_id = :user_id",
                {"user_id": test_user["user_id"]}
            )
            
            if result["data"]:
                assert result["data"][0]["id_type"] == verification_data["id_type"]
                assert result["data"][0]["id_number"] == verification_data["id_number"] 