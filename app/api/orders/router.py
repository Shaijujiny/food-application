from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.orders.schema import (
    AdminOrderCreateRequestModel,
    OrderCreateRequestModel,
    OrderStatusUpdateRequest,
)
from app.api.orders.service import OrderService
from app.database.postgresql import get_db
from app.depends.jwt_depends import (
    get_current_admin_user,
    get_current_customer_user,
    get_current_user,
)
from app.depends.language_depends import get_language
from app.utils.schemas_utils import CustomHTTPException

router = APIRouter(prefix="/orders", tags=["Orders"])


# ==========================================
# CUSTOMER ROUTES
# ==========================================
@router.post("/customer")
async def customer_create_order(
    request: OrderCreateRequestModel,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_customer_user),
    lang: str = Depends(get_language),
):
    """
    Create a new order for the authenticated customer.
    """
    return await OrderService.create_order(db, current_user.usr_id, request, lang)


@router.get("/customer")
async def customer_list_orders(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_customer_user),
    lang: str = Depends(get_language),
):
    """
    List past orders for the authenticated customer.
    """
    return await OrderService.list_orders(db, current_user.usr_id, skip, limit, lang)


@router.get("/customer/{order_uuid}")
async def customer_get_order(
    order_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_customer_user),
    lang: str = Depends(get_language),
):
    """
    View a specific order details (Customer restricted to their own).
    """
    return await OrderService.get_order(db, current_user.usr_id, order_uuid, lang)


@router.get("/customer/{order_uuid}/tracking")
async def customer_track_order(
    order_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_customer_user),
    lang: str = Depends(get_language),
):
    """
    Track order status history for a customer's specific order.
    """
    return await OrderService.track_order(db, current_user.usr_id, order_uuid, lang)


# ==========================================
# ADMIN ROUTES
# ==========================================
@router.post("/admin")
async def admin_create_order(
    request: AdminOrderCreateRequestModel,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Create an order on behalf of a specific customer.
    """
    return await OrderService.create_order(db, request.customer_id, request, lang)


@router.get("/admin")
async def admin_list_orders(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    List ALL orders in the system. Optional status filtering included.
    """
    return await OrderService.list_all_orders(db, skip, limit, status, lang)


@router.get("/admin/{order_uuid}")
async def admin_get_order(
    order_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    View ANY specific order details globally.
    """
    return await OrderService.get_any_order(db, order_uuid, lang)


@router.get("/admin/{order_uuid}/tracking")
async def admin_track_order(
    order_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Track order status history globally.
    """
    return await OrderService.track_order(db, None, order_uuid, lang)


# ==========================================
# DELIVERY & STATUS REACTION ROUTE
# ==========================================
@router.patch("/reaction/{order_uuid}/status")
async def update_order_reaction_status(
    order_uuid: str,
    request: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    lang: str = Depends(get_language),
):
    """
    Update the status of an order. Only accessible by ADMIN or DELIVERY_PARTNER.
    """
    if current_user.role not in ["ADMIN", "DELIVERY_PARTNER"]:
        raise CustomHTTPException(
            status_code=403, message="Not authorized to update order status"
        )

    return await OrderService.update_order_status(db, order_uuid, request.status, lang)
