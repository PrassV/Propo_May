from typing import Optional, List, Dict, Any, Type, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.ext.declarative import DeclarativeMeta
from app.db.supabase_db import SupabaseTable
from app.db.schema_mapper import schema_mapper
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeMeta)

class BaseRepository(Generic[T]):
    """
    Base repository class that can work with both SQLAlchemy and Supabase.
    This provides a unified interface regardless of the backend.
    """
    
    def __init__(self, model_class: Type[T], db: Optional[AsyncSession] = None, use_supabase: bool = True):
        """
        Initialize the repository.
        
        Args:
            model_class: The SQLAlchemy model class
            db: The SQLAlchemy database session (only needed if use_supabase=False)
            use_supabase: Whether to use Supabase as the backend
        """
        self.model_class = model_class
        self.db = db
        self.use_supabase = use_supabase
        
        # Setup for Supabase
        if use_supabase:
            table_name = schema_mapper.get_table_name(model_class)
            self.supabase_table = SupabaseTable(table_name)
            
            # Get PK column name for this model
            self.pk_column = schema_mapper.get_primary_key(table_name)
    
    async def create(self, data: Dict[str, Any]) -> Any:
        """Create a new record"""
        if self.use_supabase:
            return await self.supabase_table.create(data)
        else:
            # SQLAlchemy implementation
            db_obj = self.model_class(**data)
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
    
    async def get_by_id(self, record_id: UUID) -> Optional[Any]:
        """Get a record by its primary key"""
        if self.use_supabase:
            return await self.supabase_table.get_by_id(str(record_id))
        else:
            # SQLAlchemy implementation
            pk_attr = getattr(self.model_class, self.pk_column, None)
            if not pk_attr:
                pk_attr = self.model_class.id  # Default fallback
                
            query = select(self.model_class).where(pk_attr == record_id)
            result = await self.db.execute(query)
            return result.scalars().first()
    
    async def get_by_field(self, field: str, value: Any) -> Optional[Any]:
        """Get a record by a specific field value"""
        if self.use_supabase:
            return await self.supabase_table.get_by_field(field, value)
        else:
            # SQLAlchemy implementation
            field_attr = getattr(self.model_class, field)
            query = select(self.model_class).where(field_attr == value)
            result = await self.db.execute(query)
            return result.scalars().first()
    
    async def list(self, 
                  filters: Optional[Dict[str, Any]] = None,
                  skip: int = 0,
                  limit: int = 100) -> List[Any]:
        """List records with optional filters"""
        if self.use_supabase:
            return await self.supabase_table.list(filters=filters, offset=skip, limit=limit)
        else:
            # SQLAlchemy implementation
            query = select(self.model_class)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    field_attr = getattr(self.model_class, field)
                    query = query.where(field_attr == value)
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            return list(result.scalars().all())
    
    async def update(self, record_id: UUID, data: Dict[str, Any]) -> Optional[Any]:
        """Update a record by its primary key"""
        if self.use_supabase:
            return await self.supabase_table.update(str(record_id), data)
        else:
            # SQLAlchemy implementation
            pk_attr = getattr(self.model_class, self.pk_column, None)
            if not pk_attr:
                pk_attr = self.model_class.id  # Default fallback
                
            query = update(self.model_class).where(pk_attr == record_id).values(**data)
            await self.db.execute(query)
            await self.db.commit()
            
            # Return the updated object
            return await self.get_by_id(record_id)
    
    async def delete(self, record_id: UUID) -> bool:
        """Delete a record by its primary key"""
        if self.use_supabase:
            return await self.supabase_table.delete(str(record_id))
        else:
            # SQLAlchemy implementation
            pk_attr = getattr(self.model_class, self.pk_column, None)
            if not pk_attr:
                pk_attr = self.model_class.id  # Default fallback
                
            query = delete(self.model_class).where(pk_attr == record_id)
            result = await self.db.execute(query)
            await self.db.commit()
            
            # Return True if at least one row was deleted
            return result.rowcount > 0 