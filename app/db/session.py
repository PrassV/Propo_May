import warnings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config.settings import settings

# Display a deprecation warning
warnings.warn(
    "DEPRECATION WARNING: Direct database access via SQLAlchemy is deprecated. "
    "This application now uses Supabase for all data access. Please use the "
    "appropriate repository classes instead of direct database queries.",
    DeprecationWarning, stacklevel=2
)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    """
    DEPRECATED: This application now uses Supabase for all data access.
    Please use the appropriate repository classes instead of direct database queries.
    """
    warnings.warn(
        "get_db() function is deprecated. This application now uses Supabase for all data access.",
        DeprecationWarning, stacklevel=2
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 