import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base
from app.utils.schemas_utils import CustomModel


class NotificationType(str, enum.Enum):
    NEW_ORDER = "NEW_ORDER"
    NEW_USER = "NEW_USER"
    ORDER_UPDATE = "ORDER_UPDATE"
    SYSTEM = "SYSTEM"


class NotificationBaseModel(CustomModel):
    user_id: Optional[int] = None
    related_user_id: Optional[int] = None
    title: str
    message: str
    type: NotificationType
    is_read: bool = False


class TblNotifications(Base):
    __tablename__ = "tbl_notifications"
    __table_args__ = {"schema": "public"}

    notif_id: Mapped[int] = mapped_column(
        "notif_id", Integer, primary_key=True, autoincrement=True, index=True
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        "notif_user_id",
        ForeignKey("public.tbl_users.usr_id", ondelete="CASCADE"),
        nullable=True,
    )

    related_user_id: Mapped[Optional[int]] = mapped_column(
        "notif_related_user_id",
        ForeignKey("public.tbl_users.usr_id", ondelete="CASCADE"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column("notif_title", String(255), nullable=False)
    message: Mapped[str] = mapped_column("notif_message", String(1000), nullable=False)

    type: Mapped[NotificationType] = mapped_column(
        "notif_type",
        Enum(NotificationType, name="notification_type", native_enum=False, length=50),
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        "notif_is_read", Boolean, default=False, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        "notif_createdAt", DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("TblUsers", foreign_keys=[user_id], backref="notifications")
    related_user = relationship("TblUsers", foreign_keys=[related_user_id])

    @classmethod
    async def create(
        cls, data: NotificationBaseModel, db: AsyncSession
    ) -> "TblNotifications":
        notification = cls(**data.model_dump(exclude_unset=True))
        db.add(notification)
        await db.flush()
        return notification

    @classmethod
    async def mark_as_read(cls, notif_id: int, db: AsyncSession):
        result = await db.execute(select(cls).where(cls.notif_id == notif_id))
        notif = result.scalar_one_or_none()
        if notif:
            notif.is_read = True
            await db.flush()
        return notif

    @classmethod
    async def mark_all_as_read(cls, db: AsyncSession, user_id: Optional[int] = None):
        from sqlalchemy import update

        stmt = update(cls).where(cls.is_read.is_(False)).values(is_read=True)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        else:
            stmt = stmt.where(cls.user_id.is_(None))

        await db.execute(stmt)
        await db.flush()

    @classmethod
    async def get_unread_count(cls, db: AsyncSession, user_id: Optional[int] = None):
        stmt = select(func.count(cls.notif_id)).where(cls.is_read.is_(False))
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        else:
            stmt = stmt.where(cls.user_id.is_(None))
        result = await db.scalar(stmt)
        return result or 0

    @classmethod
    async def get_notifications(
        cls, db: AsyncSession, user_id: Optional[int] = None, limit: int = 50
    ):
        from sqlalchemy.orm import selectinload

        stmt = select(cls).options(selectinload(cls.related_user))
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)
        else:
            stmt = stmt.where(cls.user_id.is_(None))
        stmt = stmt.order_by(cls.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
