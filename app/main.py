from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config.settings import settings
import uvicorn

# Configure application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
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
