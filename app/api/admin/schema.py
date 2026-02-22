from datetime import datetime
from typing import Dict, List, Optional

from pydantic import EmailStr

from app.core.response.base_schema import CustomModel


class TimeSeriesData(CustomModel):
    date: str
    orders: int
    revenue: float


class RecentRestaurantSchema(CustomModel):
    name: str
    address: str
    phone: str


class RecentUserSchema(CustomModel):
    username: str
    email: str
    role: str


class RecentOrderSchema(CustomModel):
    uuid: str
    amount: float
    status: str
    created_at: datetime


class DashboardStatsResponse(CustomModel):
    restaurants: int
    categories: int
    food_items: int
    users: int
    today_orders: int
    today_revenue: float
    total_revenue: float
    total_orders: int
    status_counts: Dict[str, int]
    user_roles_counts: Dict[str, int]
    daily_stats: List[TimeSeriesData]
    weekly_stats: List[TimeSeriesData]
    monthly_stats: List[TimeSeriesData]
    three_month_stats: List[TimeSeriesData]
    yearly_stats: List[TimeSeriesData]
    recent_restaurants: List[RecentRestaurantSchema]
    recent_users: List[RecentUserSchema]
    recent_orders: List[RecentOrderSchema]
    profit_loss_status: str


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


class CreateUserRequestModel(CustomModel):
    username: str
    email: EmailStr
    password: str
    role: str = "CUSTOMER"
    is_active: bool = True
