from datetime import datetime
from typing import List, Optional

from app.core.response.base_schema import CustomModel


class NotificationResponse(CustomModel):
    notif_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(CustomModel):
    items: List[NotificationResponse]
    unread_count: int
