from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.orders.schema import (
    AdminPaginatedOrderResponse,
    OrderCreateRequestModel,
    OrderItemResponse,
    OrderResponseModel,
    PaginatedOrderResponse,
)
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.response_builder import ResponseBuilder
from app.models.main.food import TblFoods
from app.models.main.orders import (
    OrderSBaseModel,
    TblOrderItems,
    TblOrders,
    TblOrderStatusHistory,
)


class OrderService:
    @staticmethod
    async def create_order(
        db: AsyncSession, user_id: int, request: OrderCreateRequestModel, lang: str
    ):
        if not request.items:
            return ResponseBuilder.build(
                ErrorType.ERR_400_BAD_REQUEST, MessageCode.INVALID_CREDENTIALS, lang
            )

        food_ids = [item.food_id for item in request.items]
        foods = await TblFoods.get_by_ids(food_ids, db)
        food_map = {f.food_id: f for f in foods}

        total_amount = 0.0
        order_items_data = []

        for item in request.items:
            food = food_map.get(item.food_id)
            if not food or not food.is_available:
                continue

            item_price = food.price * item.quantity
            total_amount += item_price
            order_items_data.append(
                {
                    "food_id": food.food_id,
                    "quantity": item.quantity,
                    "price": food.price,
                    "food_name": food.name,
                }
            )

        if not order_items_data:
            return ResponseBuilder.build(
                ErrorType.ERR_400_BAD_REQUEST, MessageCode.INVALID_CREDENTIALS, lang
            )

        order_model = OrderSBaseModel(user_id=user_id, total_amount=total_amount)
        new_order = await TblOrders.create(order_model, db)

        saved_items = []
        for item_data in order_items_data:
            order_item = TblOrderItems(
                order_id=new_order.ord_id,
                food_id=item_data["food_id"],
                quantity=item_data["quantity"],
                price=item_data["price"],
            )
            db.add(order_item)
            saved_items.append(
                OrderItemResponse(
                    food_id=item_data["food_id"],
                    food_name=item_data["food_name"],
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )
            )

        initial_history = TblOrderStatusHistory(
            order_id=new_order.ord_id, status=new_order.status
        )
        db.add(initial_history)

        await db.flush()
        await db.commit()

        # Notify Admin
        from app.api.notifications.service import NotificationService
        from app.models.main.notifications import NotificationType

        await NotificationService.create_system_notification(
            db=db,
            title="New Order Received",
            message=f"A new order #{new_order.ord_id} has been placed for ${total_amount:.2f}.",
            type=NotificationType.NEW_ORDER,
            user_id=None,
            related_user_id=new_order.user_id,
        )

        response = OrderResponseModel(
            uuid=new_order.uuid,
            user_id=new_order.user_id,
            total_amount=new_order.total_amount,
            status=new_order.status.value,
            created_at=new_order.created_at,
            items=saved_items,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED, MessageCode.ORDER_CREATED, lang, data=response
        )

    @staticmethod
    async def list_orders(
        db: AsyncSession, user_id: int, skip: int, limit: int, lang: str
    ):
        from sqlalchemy import func

        count_stmt = select(func.count(TblOrders.ord_id)).where(
            TblOrders.user_id == user_id
        )
        total = await db.scalar(count_stmt) or 0

        stmt = (
            select(TblOrders)
            .where(TblOrders.user_id == user_id)
            .options(selectinload(TblOrders.items), selectinload(TblOrders.user))
            .order_by(TblOrders.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        orders = result.scalars().all()

        item_food_ids = list({item.food_id for order in orders for item in order.items})
        foods = await TblFoods.get_by_ids(item_food_ids, db)
        food_map = {f.food_id: f for f in foods}

        order_responses = []
        for order in orders:
            items_response = []
            for item in order.items:
                food = food_map.get(item.food_id)
                items_response.append(
                    OrderItemResponse(
                        food_id=item.food_id,
                        food_name=food.name if food else str(item.food_id),
                        quantity=item.quantity,
                        price=item.price,
                    )
                )

            order_responses.append(
                OrderResponseModel(
                    uuid=order.uuid,
                    user_id=order.user_id,
                    user_name=order.user.username
                    if getattr(order, "user", None)
                    else None,
                    total_amount=order.total_amount,
                    status=order.status.value,
                    created_at=order.created_at,
                    items=items_response,
                )
            )

        response_data = PaginatedOrderResponse(total=total, items=order_responses)

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDERS_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def get_order(db: AsyncSession, user_id: int, order_uuid: str, lang: str):
        stmt = (
            select(TblOrders)
            .where(TblOrders.user_id == user_id, TblOrders.uuid == order_uuid)
            .options(selectinload(TblOrders.items), selectinload(TblOrders.user))
        )

        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.ORDER_NOT_FOUND, lang
            )

        item_food_ids = [item.food_id for item in order.items]
        foods = await TblFoods.get_by_ids(item_food_ids, db)
        food_map = {f.food_id: f for f in foods}

        items_response = []
        for item in order.items:
            food = food_map.get(item.food_id)
            items_response.append(
                OrderItemResponse(
                    food_id=item.food_id,
                    food_name=food.name if food else str(item.food_id),
                    quantity=item.quantity,
                    price=item.price,
                )
            )

        response_data = OrderResponseModel(
            uuid=order.uuid,
            user_id=order.user_id,
            user_name=order.user.username if getattr(order, "user", None) else None,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            items=items_response,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDER_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def list_all_orders(
        db: AsyncSession, skip: int, limit: int, status: str | None, lang: str
    ):
        from sqlalchemy import func

        from app.models.main.orders import OrderStatus

        status_counts_stmt = select(
            TblOrders.status, func.count(TblOrders.ord_id)
        ).group_by(TblOrders.status)
        status_counts_result = await db.execute(status_counts_stmt)
        status_counts_raw = status_counts_result.all()

        status_counts = {s.value: 0 for s in OrderStatus}
        for stat, count in status_counts_raw:
            if stat:
                status_counts[stat.value] = count

        count_stmt = select(func.count(TblOrders.ord_id))
        stmt = (
            select(TblOrders)
            .options(selectinload(TblOrders.items), selectinload(TblOrders.user))
            .order_by(TblOrders.created_at.desc())
        )

        if status:
            try:
                status_enum = OrderStatus(status)
                count_stmt = count_stmt.where(TblOrders.status == status_enum)
                stmt = stmt.where(TblOrders.status == status_enum)
            except ValueError:
                pass

        total = await db.scalar(count_stmt) or 0
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        orders = result.scalars().all()

        item_food_ids = list({item.food_id for order in orders for item in order.items})
        foods = await TblFoods.get_by_ids(item_food_ids, db)
        food_map = {f.food_id: f for f in foods}

        order_responses = []
        for order in orders:
            items_response = []
            for item in order.items:
                food = food_map.get(item.food_id)
                items_response.append(
                    OrderItemResponse(
                        food_id=item.food_id,
                        food_name=food.name if food else str(item.food_id),
                        quantity=item.quantity,
                        price=item.price,
                    )
                )

            order_responses.append(
                OrderResponseModel(
                    uuid=order.uuid,
                    user_id=order.user_id,
                    user_name=order.user.username
                    if getattr(order, "user", None)
                    else None,
                    total_amount=order.total_amount,
                    status=order.status.value,
                    created_at=order.created_at,
                    items=items_response,
                )
            )

        response_data = AdminPaginatedOrderResponse(
            total=total, items=order_responses, status_counts=status_counts
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDERS_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def get_any_order(db: AsyncSession, order_uuid: str, lang: str):
        stmt = (
            select(TblOrders)
            .where(TblOrders.uuid == order_uuid)
            .options(selectinload(TblOrders.items), selectinload(TblOrders.user))
        )

        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.ORDER_NOT_FOUND, lang
            )

        item_food_ids = [item.food_id for item in order.items]
        foods = await TblFoods.get_by_ids(item_food_ids, db)
        food_map = {f.food_id: f for f in foods}

        items_response = []
        for item in order.items:
            food = food_map.get(item.food_id)
            items_response.append(
                OrderItemResponse(
                    food_id=item.food_id,
                    food_name=food.name if food else str(item.food_id),
                    quantity=item.quantity,
                    price=item.price,
                )
            )

        response_data = OrderResponseModel(
            uuid=order.uuid,
            user_id=order.user_id,
            user_name=order.user.username if getattr(order, "user", None) else None,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            items=items_response,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDER_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def update_order_status(
        db: AsyncSession, order_uuid: str, new_status: str, lang: str
    ):
        from app.models.main.orders import OrderStatus

        try:
            status_enum = OrderStatus(new_status)
        except ValueError:
            return ResponseBuilder.build(
                ErrorType.ERR_400_BAD_REQUEST, MessageCode.INVALID_CREDENTIALS, lang
            )

        stmt = (
            select(TblOrders)
            .where(TblOrders.uuid == order_uuid)
            .options(selectinload(TblOrders.items))
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.ORDER_NOT_FOUND, lang
            )

        order.status = status_enum

        status_history = TblOrderStatusHistory(
            order_id=order.ord_id, status=status_enum
        )
        db.add(status_history)

        await db.commit()

        # Notify Customer
        from app.api.notifications.service import NotificationService
        from app.models.main.notifications import NotificationType

        await NotificationService.create_system_notification(
            db=db,
            title="Order Status Updated",
            message=f"Your order #{order.ord_id} is now '{status_enum.value}'.",
            type=NotificationType.ORDER_UPDATE,
            user_id=order.user_id,
            related_user_id=order.user_id,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDER_STATUS_UPDATED, lang
        )

    @staticmethod
    async def track_order(
        db: AsyncSession, user_id: int | None, order_uuid: str, lang: str
    ):
        from app.api.orders.schema import (
            OrderStatusHistoryResponse,
            OrderTrackingResponseModel,
        )

        stmt = (
            select(TblOrders)
            .where(TblOrders.uuid == order_uuid)
            .options(
                selectinload(TblOrders.items),
                selectinload(TblOrders.status_history),
                selectinload(TblOrders.user),
            )
        )

        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.ORDER_NOT_FOUND, lang
            )

        if user_id is not None and order.user_id != user_id:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.ORDER_NOT_FOUND, lang
            )

        item_food_ids = [item.food_id for item in order.items]
        foods = await TblFoods.get_by_ids(item_food_ids, db)
        food_map = {f.food_id: f for f in foods}

        items_response = []
        for item in order.items:
            food = food_map.get(item.food_id)
            items_response.append(
                OrderItemResponse(
                    food_id=item.food_id,
                    food_name=food.name if food else str(item.food_id),
                    quantity=item.quantity,
                    price=item.price,
                )
            )

        history_response = sorted(
            [
                OrderStatusHistoryResponse(
                    status=h.status.value, created_at=h.created_at
                )
                for h in order.status_history
            ],
            key=lambda x: x.created_at,
        )

        response_data = OrderTrackingResponseModel(
            uuid=order.uuid,
            user_id=order.user_id,
            user_name=order.user.username if getattr(order, "user", None) else None,
            total_amount=order.total_amount,
            status=order.status.value,
            created_at=order.created_at,
            items=items_response,
            status_history=history_response,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.ORDER_FETCHED, lang, data=response_data
        )
