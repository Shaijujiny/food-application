from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel


class RestaurantBaseModel(CustomModel):
    res_id:Optional[int] = None
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


class TblRestaurants(Base):
    __tablename__ = "tbl_restaurants"
    __table_args__ = {"schema": "public"}

    res_id: Mapped[int] = mapped_column(
        "res_id",
        Integer,
        primary_key=True,
        autoincrement=True
    )

    uuid: Mapped[str] = mapped_column(
        "res_uuid",
        String(36),
        default=lambda: str(uuid4()),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        "res_name",
        String(200),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        "res_address",
        String(500),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        "res_phone",
        String(20),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        "res_isActive",
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        "res_createdAt",
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    @classmethod
    async def create(cls, data: RestaurantBaseModel, db: AsyncSession):
        restaurant = cls(**data.model_dump(exclude_unset=True))
        db.add(restaurant)
        await db.flush()
        await db.refresh(restaurant)
        return restaurant


    @classmethod
    async def active_restaurants_count(cls, db: AsyncSession):
        result = await db.scalar(
            select(func.count(cls.res_id)).where(cls.is_active == True)
        )
        return result or 0
    @classmethod
    async def get_recent(cls, db: AsyncSession, limit: int = 5):
        result = await db.execute(
            select(cls).order_by(cls.created_at.desc()).limit(limit)
        )
        return result.scalars().all()
