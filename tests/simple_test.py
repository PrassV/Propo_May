import httpx
import asyncio
import pytest
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoint base URL
API_URL = "https://propomay-production.up.railway.app/api"

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoints without authentication."""
    logger.info("Testing unauthorized access to protected endpoints")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # List of protected endpoints to test
        protected_endpoints = [
            "/users/me",  # Get current user profile
            "/users",     # List all users
            "/properties" # List properties
        ]
        
        # Test each protected endpoint
        for endpoint in protected_endpoints:
            logger.info(f"Testing unauthorized access to {endpoint}")
            response = await client.get(f"{API_URL}{endpoint}")
            logger.info(f"Response status: {response.status_code}")
            
            # Verify access is denied with 401
            assert response.status_code == 401, f"Endpoint {endpoint} should return 401 Unauthorized"
            
            # Verify response contains error detail
            response_data = response.json()
            assert "detail" in response_data, f"Response should contain error detail"
            
            logger.info(f"Unauthorized access test passed for {endpoint}")
        
        logger.info("All unauthorized access tests passed successfully")

@pytest.mark.asyncio
async def test_api_server_availability():
    """Test that the API server is available and responding."""
    logger.info("Testing API server availability")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Try to access the root API endpoint
            response = await client.get(API_URL.replace("/api", "/"))
            logger.info(f"API server responded with status: {response.status_code}")
            
            # We just care that the server responds, not about the specific status code
            assert response.status_code != 0, "API server should respond"
            logger.info("API server is available")
        except Exception as e:
            logger.error(f"Error connecting to API server: {str(e)}")
            assert False, "API server should be reachable"

@pytest.mark.asyncio
async def test_password_reset_request():
    """Test that the password reset endpoint responds."""
    logger.info("Testing password reset request endpoint")
    
    # We don't expect this to actually send an email, just checking the endpoint exists
    test_email = f"test_{uuid.uuid4()}@example.com"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_URL}/auth/forgot-password",
            json={"email": test_email}
        )
        
        logger.info(f"Password reset response status: {response.status_code}")
        
        # Endpoint should return success even if email doesn't exist (security best practice)
        assert response.status_code == 200, "Password reset endpoint should return 200 OK"
        
        # Verify response format
        response_data = response.json()
        assert "success" in response_data, "Response should contain success flag"
        
        logger.info("Password reset endpoint test passed successfully")

@pytest.mark.asyncio
async def test_login_endpoint_exists():
    """Test that the login endpoint exists and responds appropriately to invalid credentials."""
    logger.info("Testing login endpoint exists")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{API_URL}/auth/login",
            data={"username": "invalid@example.com", "password": "invalidpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        logger.info(f"Login endpoint response status: {response.status_code}")
        
        # Should return 401 for invalid credentials, not 404
        assert response.status_code == 401, "Login with invalid credentials should return 401"
        
        # Verify response contains error detail
        response_data = response.json()
        assert "detail" in response_data, "Response should contain error detail"
        
        logger.info("Login endpoint test passed successfully")

@pytest.mark.asyncio
async def test_api_endpoints_exist():
    """Test that key API endpoints exist by checking their OPTIONS response."""
    logger.info("Testing API endpoints existence")
    
    endpoints_to_check = [
        "/auth/register",
        "/auth/login",
        "/auth/refresh",
        "/users/me",
        "/properties"
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints_to_check:
            logger.info(f"Checking if endpoint exists: {endpoint}")
            
            # Using OPTIONS request to check if endpoint exists
            response = await client.options(f"{API_URL}{endpoint}")
            
            # We don't care about the specific status code, just that it's not 404
            logger.info(f"OPTIONS response for {endpoint}: {response.status_code}")
            assert response.status_code != 404, f"Endpoint {endpoint} should exist"
            
        logger.info("All endpoints existence check passed successfully") 