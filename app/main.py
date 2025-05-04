from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config.settings import settings
from app.core.errors.supabase_error_handler import SupabaseErrorHandler, SupabaseError
from app.db.supabase_config import configure_supabase_auth_urls, customize_email_templates
import uvicorn
import logging
from fastapi_mcp import FastApiMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Configure application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Set up CORS with appropriate configuration
allowed_origins = [
    "https://propomay-production.up.railway.app",  # Railway production URL
    "http://localhost:3000",  # Local frontend development
]

# Add wildcard only in development mode
if settings.DEBUG:
    logger = logging.getLogger(__name__)
    logger.warning("Running in DEBUG mode with permissive CORS settings. This is not recommended for production.")
    # Instead of *, add specific development-only domains
    allowed_origins.extend([
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Supabase exception handler
app.add_exception_handler(SupabaseError, SupabaseErrorHandler.handle_exception)
app.add_exception_handler(Exception, SupabaseErrorHandler.handle_exception)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Property Management Portal API",
        "docs": f"{settings.BASE_URL}/docs",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    # Simple health check endpoint for Railway
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    """Execute tasks when the application starts up"""
    logger.info("Executing startup tasks...")
    
    # Configure Supabase Auth URLs and email templates
    if settings.SUPABASE_SERVICE_ROLE_KEY:
        await configure_supabase_auth_urls()
        await customize_email_templates()
    else:
        logger.warning(
            "SUPABASE_SERVICE_ROLE_KEY not provided. "
            "Cannot configure Supabase Auth URLs or email templates. "
            "Email confirmations will use default redirect URLs and templates."
        )

    
mcp = FastApiMCP(
    app,  
    name="Auth MCP",  
    description="MCP server for my Auth API",  # Description
    base_url="https://propomay-production.up.railway.app",  # Where your API is running
    describe_all_responses=True,  # Include all possible response schemas
    describe_full_response_schema=True,
    include_tags=["authentication", "users"]
)

mcp.mount()

if __name__ == "__main__":
    # Run with uvicorn when executed directly
    uvicorn.run("app.main:app", 
                host=settings.APP_HOST, 
                port=settings.APP_PORT,
                reload=settings.DEBUG)
