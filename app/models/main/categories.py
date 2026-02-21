from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel

class CategoryBaseModel(CustomModel):
    cat_id:Optional[int]=None
    name: Optional[str] = None
    restaurant_id: Optional[int] = None



class TblCategories(Base):
    __tablename__ = "tbl_categories"
    __table_args__ = {"schema": "public"}

    cat_id: Mapped[int] = mapped_column(
        "cat_id",
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        "cat_name",
        String(150),
        nullable=False
    )

    restaurant_id: Mapped[int] = mapped_column(
        "cat_restaurant_id",
        ForeignKey("public.tbl_restaurants.res_id", ondelete="CASCADE"),
        nullable=False
    )


    @classmethod
    async def create(cls, data: CategoryBaseModel, db: AsyncSession):
        category = cls(**data.model_dump(exclude_unset=True))
        db.add(category)
        await db.flush()
        await db.refresh(category)
        return category
    
    @classmethod
    async def active_categories_count(cls, db: AsyncSession):
        result = await db.scalar(
            select(func.count(cls.cat_id))
        )
        return result or 0