from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel


class FoodSBaseModel(CustomModel):
    food_id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    is_available: Optional[bool] = True
    image_data: Optional[str] = None


class TblFoods(Base):
    __tablename__ = "tbl_foods"
    __table_args__ = {"schema": "public"}

    food_id: Mapped[int] = mapped_column(
        "food_id", Integer, primary_key=True, autoincrement=True
    )

    name: Mapped[str] = mapped_column("food_name", String(200), nullable=False)

    price: Mapped[float] = mapped_column("food_price", Float, nullable=False)

    category_id: Mapped[int] = mapped_column(
        "food_category_id",
        ForeignKey("public.tbl_categories.cat_id", ondelete="CASCADE"),
        nullable=False,
    )

    is_available: Mapped[bool] = mapped_column(
        "food_isAvailable", Boolean, default=True, nullable=False
    )

    image_data: Mapped[Optional[str]] = mapped_column("food_image", Text, nullable=True)

    # -------------------------
    # Queries
    # -------------------------
    @classmethod
    async def get_by_category(cls, category_id: int, db: AsyncSession):
        result = await db.execute(select(cls).where(cls.category_id == category_id))
        return result.scalars().all()

    @classmethod
    async def get_by_ids(cls, food_ids: list[int], db: AsyncSession):
        result = await db.execute(select(cls).where(cls.food_id.in_(food_ids)))
        return result.scalars().all()

    @classmethod
    async def create(cls, data: FoodSBaseModel, db: AsyncSession):
        food = cls(**data.model_dump(exclude_unset=True))
        db.add(food)
        await db.flush()
        await db.refresh(food)
        return food

    @classmethod
    async def active_foods_count(cls, db: AsyncSession):
        result = await db.scalar(
            select(func.count(cls.food_id)).where(cls.is_available)
        )
        return result or 0
