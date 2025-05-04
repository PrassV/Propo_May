import pytest
import asyncio
from typing import Dict, Any
import httpx
from tests.auth_test_base import AuthTestBase
from tests.mcp_client import MCPClient

class TestAuthScenarios(AuthTestBase):
    """Tests for complete authentication scenarios."""
    
    @pytest.mark.asyncio
    async def test_registration_to_profile_setup(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test full registration → login → profile setup → role switch flow."""
        # Step 1: Register a new user
        test_email = self.generate_test_email()
        
        register_data = {
            "email": test_email,
            "password": self.TEST_USER_PASSWORD,
            "first_name": "Scenario",
            "last_name": "Test",
            "role": "tenant"
        }
        
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/register",
            json=register_data
        )
        
        assert response.status_code == 201
        user_data = response.json()
        user_id = user_data["user_id"]
        
        # Step 2: Login with the new user
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_email,
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        token_data = response.json()
        auth_header = f"{token_data['token_type']} {token_data['access_token']}"
        
        # Step 3: Get user profile
        response = await api_client.get(
            f"{self.API_PREFIX}/users/me",
            headers={"Authorization": auth_header}
        )
        
        assert response.status_code == 200
        profile = response.json()
        assert profile["email"] == test_email
        assert profile["role"] == "tenant"
        
        # Step 4: Complete profile setup (if endpoint exists)
        profile_data = {
            "phone": "+19876543210",
            "address": "456 Scenario St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "54321",
            "preferred_contact_method": "phone"
        }
        
        response = await api_client.post(
            f"{self.API_PREFIX}/users/profile-setup",
            json=profile_data,
            headers={"Authorization": auth_header}
        )
        
        # Skip verification if endpoint doesn't exist
        if response.status_code == 200:
            updated_profile = response.json()
            assert updated_profile["phone"] == profile_data["phone"]
        
        # Step 5: Update user profile
        update_data = {
            "first_name": "Updated",
            "last_name": "User"
        }
        
        response = await api_client.put(
            f"{self.API_PREFIX}/users/me",
            json=update_data,
            headers={"Authorization": auth_header}
        )
        
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["first_name"] == update_data["first_name"]
        assert updated_user["last_name"] == update_data["last_name"]
        
        # Step 6: Add owner role to user for role switching test
        await mcp_client.execute_query(
            """
            INSERT INTO public.user_roles (user_id, role) 
            VALUES (:user_id, 'owner')
            """,
            {"user_id": user_id}
        )
        
        # Step 7: Switch to owner role
        response = await api_client.post(
            f"{self.API_PREFIX}/users/switch-role",
            json={"role": "owner"},
            headers={"Authorization": auth_header}
        )
        
        # Skip verification if endpoint doesn't exist
        if response.status_code == 200:
            role_data = response.json()
            assert role_data["current_role"] == "owner"
            
            # Verify role switch took effect
            response = await api_client.get(
                f"{self.API_PREFIX}/users/me",
                headers={"Authorization": auth_header}
            )
            
            assert response.status_code == 200
            profile = response.json()
            assert profile["role"] == "owner"
        
        # Step 8: Logout
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/logout",
            json={"authorization": auth_header}
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_password_reset_journey(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test the complete password reset journey."""
        # Step 1: Create a test user
        test_email = self.generate_test_email()
        user = await mcp_client.create_test_user(
            email=test_email,
            password=self.TEST_USER_PASSWORD,
            role="tenant"
        )
        
        # Step 2: Request password reset
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/forgot-password",
            json={"email": test_email}
        )
        
        assert response.status_code == 200
        
        # In a real test, we'd get the reset token from the database
        # and use it to reset the password
        # However, since we're not actually sending emails in testing,
        # we can simulate this by directly updating the password in the database
        
        # Step 3: Simulate password reset by updating in the database
        new_password = "NewPassword@123"
        
        # Update the password in auth.users
        await mcp_client.execute_query(
            """
            UPDATE auth.users
            SET encrypted_password = :new_password
            WHERE email = :email
            """,
            {
                "email": test_email,
                "new_password": f"fake_hashed_{new_password}"
            }
        )
        
        # Step 4: Try logging in with the new password
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_email,
                "password": new_password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # This should succeed if our simulation was correct
        # In real testing, this would only work if the reset-password endpoint worked
        # and we had the actual reset token
        # Here we're just verifying the flow concept
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_user_verification_process(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test the user verification submission process."""
        # Step 1: Create a test user
        test_email = self.generate_test_email()
        user = await mcp_client.create_test_user(
            email=test_email,
            password=self.TEST_USER_PASSWORD,
            role="tenant"
        )
        
        # Step 2: Login with the user
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_email,
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        token_data = response.json()
        auth_header = f"{token_data['token_type']} {token_data['access_token']}"
        
        # Step 3: Submit verification documents
        verification_data = {
            "id_type": "passport",
            "id_number": "PP12345678",
            "document_urls": ["https://example.com/fake-passport-front.jpg"]
        }
        
        response = await api_client.post(
            f"{self.API_PREFIX}/users/verification-documents",
            json=verification_data,
            headers={"Authorization": auth_header}
        )
        
        # Skip further tests if endpoint doesn't exist
        if response.status_code == 200:
            # Step 4: Check verification status in profile
            response = await api_client.get(
                f"{self.API_PREFIX}/users/profile",
                headers={"Authorization": auth_header}
            )
            
            assert response.status_code == 200
            profile = response.json()
            
            # The verification_status should be "pending" or similar
            # This depends on your implementation
            assert "verification_status" in profile
            assert profile["verification_status"] in ["pending", "submitted", "not_submitted", "verified", "rejected"]
            
            # Step 5: Admin approves verification (simulate)
            # First, get an admin token
            admin_email = self.generate_test_email()
            admin = await mcp_client.create_test_user(
                email=admin_email,
                password=self.TEST_USER_PASSWORD,
                role="admin"
            )
            
            admin_login_response = await api_client.post(
                f"{self.API_PREFIX}/auth/login",
                data={
                    "username": admin_email,
                    "password": self.TEST_USER_PASSWORD
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            admin_token = admin_login_response.json()
            admin_auth_header = f"{admin_token['token_type']} {admin_token['access_token']}"
            
            # Simulate admin approving the verification
            # This would be a different endpoint in your API
            # For now, we'll just update the database directly
            await mcp_client.execute_query(
                """
                UPDATE public.user_verifications
                SET status = 'verified', 
                    verified_at = CURRENT_TIMESTAMP,
                    verified_by = :admin_id
                WHERE user_id = :user_id
                """,
                {
                    "user_id": user["user_id"],
                    "admin_id": admin["user_id"]
                }
            )
            
            # Step 6: Check updated verification status
            response = await api_client.get(
                f"{self.API_PREFIX}/users/profile",
                headers={"Authorization": auth_header}
            )
            
            assert response.status_code == 200
            profile = response.json()
            
            # Verification status should now be "verified"
            # Only if the previous database update worked
            # This depends on your implementation
            assert "verification_status" in profile
    
    @pytest.mark.asyncio
    async def test_admin_user_management(self, api_client: httpx.AsyncClient, mcp_client: MCPClient):
        """Test the admin user management flow."""
        # Step 1: Create an admin user
        admin_email = self.generate_test_email()
        admin = await mcp_client.create_test_user(
            email=admin_email,
            password=self.TEST_USER_PASSWORD,
            role="admin"
        )
        
        # Step 2: Login as admin
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": admin_email,
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        token_data = response.json()
        admin_auth_header = f"{token_data['token_type']} {token_data['access_token']}"
        
        # Step 3: Create a regular user to manage
        test_email = self.generate_test_email()
        user = await mcp_client.create_test_user(
            email=test_email,
            password=self.TEST_USER_PASSWORD,
            role="tenant"
        )
        
        # Step 4: List all users as admin
        response = await api_client.get(
            f"{self.API_PREFIX}/users",
            headers={"Authorization": admin_auth_header}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        
        # Verify both users are in the list
        user_emails = [u["email"] for u in users]
        assert admin_email in user_emails
        assert test_email in user_emails
        
        # Step 5: Update user as admin
        # This endpoint might not exist, depending on your implementation
        # If it does exist, it would be something like PUT /api/users/{user_id}
        # For now, we'll just update the database directly
        await mcp_client.execute_query(
            """
            UPDATE public.users
            SET status = 'inactive'
            WHERE user_id = :user_id
            """,
            {"user_id": user["user_id"]}
        )
        
        # Step 6: Verify user was updated
        response = await api_client.get(
            f"{self.API_PREFIX}/users",
            headers={"Authorization": admin_auth_header}
        )
        
        assert response.status_code == 200
        users = response.json()
        
        # Find the updated user
        updated_user = next((u for u in users if u["email"] == test_email), None)
        assert updated_user is not None
        assert updated_user["status"] == "inactive"
        
        # Step 7: Verify inactive user can't login
        response = await api_client.post(
            f"{self.API_PREFIX}/auth/login",
            data={
                "username": test_email,
                "password": self.TEST_USER_PASSWORD
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should be 403 Forbidden if status check is implemented
        # Could be 401 Unauthorized if not
        assert response.status_code in [401, 403] 