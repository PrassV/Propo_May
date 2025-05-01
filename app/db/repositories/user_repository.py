from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.user import User, UserRole
from app.core.security.auth import get_password_hash, verify_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user_data: dict) -> User:
        # Hash password if present and not already hashed
        if "password" in user_data and "password_hash" not in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        
        db_user = User(**user_data)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    async def get_by_supabase_uid(self, supabase_uid: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.supabase_uid == supabase_uid))
        return result.scalars().first()
    
    async def list(self, skip: int = 0, limit: int = 100, role: Optional[UserRole] = None) -> List[User]:
        query = select(User)
        if role:
            query = query.where(User.role == role)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        # Hash password if present
        if "password" in user_data:
            user_data["password_hash"] = get_password_hash(user_data.pop("password"))
            
        await self.db.execute(
            update(User).where(User.id == user_id).values(**user_data)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: UUID) -> None:
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user 