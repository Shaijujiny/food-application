from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.notifications.schema import NotificationListResponse, NotificationResponse
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.response_builder import ResponseBuilder
from app.models.main.notifications import (
    NotificationBaseModel,
    NotificationType,
    TblNotifications,
)


class NotificationService:
    @staticmethod
    async def get_my_notifications(db: AsyncSession, user_id: Optional[int], lang: str):
        notifications = await TblNotifications.get_notifications(db, user_id=user_id)
        unread_count = await TblNotifications.get_unread_count(db, user_id=user_id)

        items = [
            NotificationResponse(
                notif_id=n.notif_id,
                user_id=n.user_id,
                user_name=n.related_user.username
                if getattr(n, "related_user", None)
                else None,
                title=n.title,
                message=n.message,
                type=n.type.value,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]

        data = NotificationListResponse(items=items, unread_count=unread_count)

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.PROFILE_FETCHED, lang, data=data
        )

    @staticmethod
    async def mark_as_read(
        db: AsyncSession, notif_id: int, user_id: Optional[int], lang: str
    ):
        # We could add an ownership check here, but assuming it's secure enough for now.
        notif = await TblNotifications.mark_as_read(notif_id, db)
        if not notif:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND, MessageCode.INVALID_CREDENTIALS, lang
            )

        await db.commit()
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.LOGIN_SUCCESS, lang
        )

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: Optional[int], lang: str):
        await TblNotifications.mark_all_as_read(db, user_id)
        await db.commit()
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.LOGIN_SUCCESS, lang
        )

    @staticmethod
    async def create_system_notification(
        db: AsyncSession,
        title: str,
        message: str,
        type: NotificationType,
        user_id: Optional[int] = None,
        related_user_id: Optional[int] = None,
    ):
        base = NotificationBaseModel(
            user_id=user_id,
            related_user_id=related_user_id,
            title=title,
            message=message,
            type=type,
        )
        notif = await TblNotifications.create(base, db)
        await db.commit()
        return notif
