


from datetime import datetime
from uuid import uuid4

from pydantic import Field
from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy_utils import StringEncryptedType, UUIDType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.annotations import DB_STRING_ENCRYPTION
from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel

SECRET_KEY = "mysecretkey123" 
class UsersBaseModel(CustomModel):
    """Base model for user-related data."""

    username: str | None = Field(default=None)
    email: str | None = Field(default=None)
    hashed_password: str | None = Field(default=None)
    is_active: bool | None = Field(default=True)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class TblUsers(Base):
    __tablename__ = "users"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    username = Column(String, unique=True, index=True, nullable=False)

    email = Column(StringEncryptedType(DB_STRING_ENCRYPTION), unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    async def create(cls, data: UsersBaseModel,db: AsyncSession):
        """Create new record."""
        data_dict = data.model_dump()
        new_data = cls(**data_dict)
        db.add(new_data)
        await db.flush()
        return new_data