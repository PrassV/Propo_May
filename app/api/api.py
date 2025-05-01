from fastapi import APIRouter
from app.api.endpoints import auth, properties, units, users, dashboard, maintenance

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(units.router, prefix="/units", tags=["units"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])

# Additional routers to be implemented:
# api_router.include_router(leases.router, prefix="/leases", tags=["leases"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"]) 