from datetime import datetime
from typing import Dict, List

from app.core.response.base_schema import CustomModel


class OrderItemRequest(CustomModel):
    food_id: int
    quantity: int = 1


class OrderCreateRequestModel(CustomModel):
    items: List[OrderItemRequest]


class AdminOrderCreateRequestModel(OrderCreateRequestModel):
    customer_id: int


class OrderItemResponse(CustomModel):
    food_id: int
    food_name: str
    quantity: int
    price: float


class OrderResponseModel(CustomModel):
    uuid: str
    user_id: int
    user_name: str | None = None
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []


class PaginatedOrderResponse(CustomModel):
    total: int
    items: List[OrderResponseModel]


class AdminPaginatedOrderResponse(PaginatedOrderResponse):
    status_counts: Dict[str, int]


class OrderStatusUpdateRequest(CustomModel):
    status: str


class OrderStatusHistoryResponse(CustomModel):
    status: str
    created_at: datetime


class OrderTrackingResponseModel(OrderResponseModel):
    status_history: List[OrderStatusHistoryResponse] = []
