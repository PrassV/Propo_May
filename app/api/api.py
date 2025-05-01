from fastapi import APIRouter
from app.api.endpoints import auth, properties, units, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, prefix="/properties", tags=["properties"])
api_router.include_router(units.router, prefix="/units", tags=["units"])
# Include other routers as they are created:
# api_router.include_router(leases.router, prefix="/leases", tags=["leases"])
# api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
# ... and so on 