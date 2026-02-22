import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


# ===============================
# Pydantic Base Schema
# ===============================
class OrderSBaseModel(CustomModel):
    user_id: int
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING


# ===============================
# SQLAlchemy Models
# ===============================
class TblOrders(Base):
    __tablename__ = "tbl_orders"
    __table_args__ = {"schema": "public"}

    ord_id: Mapped[int] = mapped_column(
        "ord_id", Integer, primary_key=True, autoincrement=True, index=True
    )

    uuid: Mapped[str] = mapped_column(
        "ord_uuid",
        String(36),
        default=lambda: str(uuid4()),
        nullable=False,
        unique=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        "ord_user_id",
        ForeignKey("public.tbl_users.usr_id", ondelete="CASCADE"),
        nullable=False,
    )

    total_amount: Mapped[float] = mapped_column(
        "ord_totalAmount", Float, nullable=False, default=0.0
    )

    status: Mapped[OrderStatus] = mapped_column(
        "ord_status",
        Enum(OrderStatus, name="order_status", native_enum=False, length=50),
        default=OrderStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        "ord_createdAt", DateTime, default=datetime.utcnow, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        "ord_updatedAt",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    items = relationship(
        "TblOrderItems", back_populates="order", cascade="all, delete-orphan"
    )
    user = relationship("TblUsers", backref="orders")
    status_history = relationship(
        "TblOrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )

    @classmethod
    async def create(cls, data: OrderSBaseModel, db: AsyncSession) -> "TblOrders":
        order = cls(**data.model_dump(exclude_unset=True))
        db.add(order)
        await db.flush()
        await db.refresh(order)
        return order

    @classmethod
    async def get_by_uuid(
        cls, ord_uuid: str, db: AsyncSession
    ) -> Optional["TblOrders"]:
        result = await db.execute(select(cls).where(cls.uuid == ord_uuid))
        return result.scalar_one_or_none()

    @classmethod
    async def get_dashboard_order_stats(cls, db: AsyncSession):
        from sqlalchemy import func

        stmt = select(
            cls.status,
            func.count(cls.ord_id),
            func.sum(cls.total_amount),
        ).group_by(cls.status)
        result = await db.execute(stmt)
        return result.all()

    @classmethod
    async def get_stats_in_range(
        cls, db: AsyncSession, start_date: datetime, end_date: datetime = None
    ):
        from sqlalchemy import func

        stmt = select(func.count(cls.ord_id), func.sum(cls.total_amount)).where(
            cls.created_at >= start_date
        )
        if end_date:
            stmt = stmt.where(cls.created_at < end_date)
        result = await db.execute(stmt)
        return result.one()

    @classmethod
    async def get_timeseries_stats(
        cls, db: AsyncSession, interval: str, start_date: datetime
    ):
        from sqlalchemy import func

        stmt = (
            select(
                func.date_trunc(interval, cls.created_at).label("bucket"),
                func.count(cls.ord_id),
                func.sum(cls.total_amount),
            )
            .where(cls.created_at >= start_date)
            .group_by("bucket")
            .order_by("bucket")
        )
        result = await db.execute(stmt)
        return result.all()

    @classmethod
    async def get_recent_orders(cls, db: AsyncSession, limit: int = 5):
        stmt = select(cls).order_by(cls.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()


class TblOrderItems(Base):
    __tablename__ = "tbl_order_items"
    __table_args__ = {"schema": "public"}

    item_id: Mapped[int] = mapped_column(
        "item_id", Integer, primary_key=True, autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        "item_order_id",
        ForeignKey("public.tbl_orders.ord_id", ondelete="CASCADE"),
        nullable=False,
    )

    food_id: Mapped[int] = mapped_column(
        "item_food_id",
        ForeignKey("public.tbl_foods.food_id", ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        "item_quantity", Integer, nullable=False, default=1
    )

    price: Mapped[float] = mapped_column("item_price", Float, nullable=False)

    # Relationship back to order
    order = relationship("TblOrders", back_populates="items")


class TblOrderStatusHistory(Base):
    __tablename__ = "tbl_order_status_history"
    __table_args__ = {"schema": "public"}

    history_id: Mapped[int] = mapped_column(
        "history_id", Integer, primary_key=True, autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        "history_order_id",
        ForeignKey("public.tbl_orders.ord_id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[OrderStatus] = mapped_column(
        "history_status",
        Enum(OrderStatus, name="order_status", native_enum=False, length=50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        "history_createdAt", DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship back to order
    order = relationship("TblOrders", back_populates="status_history")
