import enum
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"


# ===============================
# Pydantic Base Schema
# ===============================
class UsersBaseModel(CustomModel):
    username: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = True


# ===============================
# SQLAlchemy Model
# ===============================
class TblUsers(Base):
    __tablename__ = "tbl_users"
    __table_args__ = {"schema": "public"}  # Prevent schema error

    # -------------------------------
    # Primary Key
    # -------------------------------
    usr_id: Mapped[int] = mapped_column(
        "usr_id", Integer, primary_key=True, autoincrement=True, index=True
    )

    # -------------------------------
    # UUID (Used in JWT)
    # -------------------------------
    uuid: Mapped[str] = mapped_column(
        "usr_uuid",
        String(36),
        default=lambda: str(uuid4()),
        nullable=False,
        unique=True,
        index=True,
    )

    # -------------------------------
    # User Fields
    # -------------------------------
    username: Mapped[str] = mapped_column(
        "usr_username", String(150), unique=True, nullable=False
    )

    email: Mapped[str] = mapped_column(
        "usr_email", String(255), unique=True, nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        "usr_hashedPassword", String(255), nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        "usr_role",
        Enum(UserRole, name="user_role", native_enum=False, length=50),
        default=UserRole.CUSTOMER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        "usr_isActive", Boolean, default=True, nullable=False
    )

    # -------------------------------
    # Timestamps
    # -------------------------------
    created_at: Mapped[datetime] = mapped_column(
        "usr_createdAt", DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        "usr_updatedAt",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ===============================
    # Create User
    # ===============================
    @classmethod
    async def create(cls, data: UsersBaseModel, db: AsyncSession) -> "TblUsers":

        user = cls(**data.model_dump(exclude_unset=True))
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    # ===============================
    # Get By Username
    # ===============================
    @classmethod
    async def get_by_username(
        cls, username: str, db: AsyncSession
    ) -> Optional["TblUsers"]:

        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar_one_or_none()

    # ===============================
    # Get By UUID
    # ===============================
    @classmethod
    async def get_by_uuid(
        cls, user_uuid: str, db: AsyncSession
    ) -> Optional["TblUsers"]:

        result = await db.execute(select(cls).where(cls.uuid == user_uuid))
        return result.scalar_one_or_none()

    # ===============================
    # Get By ID
    # ===============================
    @classmethod
    async def get_by_id(cls, uuid: str, db: AsyncSession) -> Optional["TblUsers"]:

        result = await db.execute(select(cls).where(cls.uuid == uuid))
        return result.scalar_one_or_none()

    # ===============================
    # Get Total Users Count
    # ===============================
    @classmethod
    async def total_users_count(cls, db: AsyncSession) -> int:
        from sqlalchemy import func

        result = await db.scalar(select(func.count(cls.usr_id)))
        return result or 0

    @classmethod
    async def get_recent(
        cls, db: AsyncSession, limit: int = 5, role: Optional[UserRole] = None
    ):
        stmt = select(cls)
        if role:
            stmt = stmt.where(cls.role == role)
        result = await db.execute(stmt.order_by(cls.created_at.desc()).limit(limit))
        return result.scalars().all()

    @classmethod
    async def list_users(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        role: Optional[UserRole] = None,
    ) -> tuple[int, List["TblUsers"]]:
        from sqlalchemy import func

        stmt = select(cls)
        count_stmt = select(func.count(cls.usr_id))

        if role:
            stmt = stmt.where(cls.role == role)
            count_stmt = count_stmt.where(cls.role == role)

        total = await db.scalar(count_stmt)
        total = total or 0

        result = await db.execute(
            stmt.order_by(cls.created_at.desc()).offset(skip).limit(limit)
        )
        users = result.scalars().all()

        return total, users

    async def update(self, db: AsyncSession, data: dict) -> "TblUsers":
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self

    async def delete(self, db: AsyncSession) -> None:
        await db.delete(self)
        await db.commit()
