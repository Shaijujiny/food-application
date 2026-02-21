# app/api/admin/schema.py

from typing import List, Optional

from pydantic import EmailStr

from app.core.response.base_schema import CustomModel


class DashboardStatsResponse(CustomModel):
    restaurants: int
    categories: int
    food_items: int
    users: int
    growth: float
    total_revenue: float
    total_orders: int
    pending_orders: int
    completed_orders: int
    recent_restaurants: list
    recent_users: list


class AdminProfileResponse(CustomModel):
    username: str
    email: str
    role: str


class UserResponseModel(CustomModel):
    uuid: str
    username: str
    email: str
    role: str
    is_active: bool


class PaginatedUserResponse(CustomModel):
    total: int
    items: List[UserResponseModel]


class UpdateUserRequestModel(CustomModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
