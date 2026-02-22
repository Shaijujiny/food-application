from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.notifications.schema import NotificationListResponse
from app.api.notifications.service import NotificationService
from app.core.response.base_schema import CustomResponse
from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/admin", response_model=CustomResponse[NotificationListResponse])
async def get_admin_notifications(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Get method only for alerts to Admin (New order, New customer).
    """
    # admin notifications have user_id = None
    return await NotificationService.get_my_notifications(db, None, lang)


@router.patch("/admin/mark-all-read", response_model=CustomResponse)
async def mark_all_admin_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Mark all admin notifications as read.
    """
    # admin notifications have user_id = None
    return await NotificationService.mark_all_as_read(db, None, lang)
