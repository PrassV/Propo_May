from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config.settings import settings
from app.core.errors.supabase_error_handler import SupabaseErrorHandler, SupabaseError
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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
    "*" if settings.DEBUG else None,  # Allow all origins in development
]

# Remove None values
allowed_origins = [origin for origin in allowed_origins if origin]

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

if __name__ == "__main__":
    # Run with uvicorn when executed directly
    uvicorn.run("app.main:app", 
                host=settings.APP_HOST, 
                port=settings.APP_PORT,
                reload=settings.DEBUG)
