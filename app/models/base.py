from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps to models"""
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    """Base mixin for UUID primary keys. 
    Child classes should override this with a specific column name."""
    pass

# Helper method for defining UUID primary keys with custom names
def uuid_pk(column_name="id"):
    return Column(column_name, UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 