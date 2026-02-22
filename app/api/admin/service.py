# app/api/admin/service.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.schema import AdminProfileResponse, DashboardStatsResponse
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.response_builder import ResponseBuilder
from app.models.main.categories import TblCategories
from app.models.main.food import TblFoods
from app.models.main.restaurants import TblRestaurants


class DashboardService:
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession, lang: str):
        from datetime import datetime, timedelta, timezone

        from app.api.admin.schema import (
            RecentOrderSchema,
            RecentRestaurantSchema,
            RecentUserSchema,
            TimeSeriesData,
        )
        from app.models.main.orders import OrderStatus, TblOrders
        from app.models.main.users import TblUsers, UserRole

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Basic counts from existing model methods
        restaurants = await TblRestaurants.active_restaurants_count(db)
        categories = await TblCategories.active_categories_count(db)
        food_items = await TblFoods.active_foods_count(db)
        users = await TblUsers.total_users_count(db)
        recent_res = await TblRestaurants.get_recent(db)
        recent_usr = await TblUsers.get_recent(db, role=UserRole.CUSTOMER)

        # Order totals and revenue via model methods
        all_order_stats = await TblOrders.get_dashboard_order_stats(db)
        status_counts = {}
        total_orders = 0
        total_revenue = 0.0
        for status, count, amount in all_order_stats:
            if status:
                status_counts[status.value] = count
                total_orders += count
                if status == OrderStatus.DELIVERED:
                    total_revenue += float(amount) if amount else 0.0

        # Today's performance via model methods
        today_count, today_revenue_sum = await TblOrders.get_stats_in_range(
            db, today_start
        )
        today_orders = today_count or 0
        today_revenue = float(today_revenue_sum) if today_revenue_sum else 0.0

        # Chart Data Segments via model methods
        # Daily
        last_7_days = today_start - timedelta(days=6)
        daily_raw = await TblOrders.get_timeseries_stats(db, "day", last_7_days)
        daily_stats = [
            TimeSeriesData(
                date=str(row[0].date()),
                orders=row[1],
                revenue=float(row[2]) if row[2] else 0.0,
            )
            for row in daily_raw
        ]

        # Weekly
        last_4_weeks = today_start - timedelta(weeks=4)
        weekly_raw = await TblOrders.get_timeseries_stats(db, "week", last_4_weeks)
        weekly_stats = [
            TimeSeriesData(
                date=f"Week {row[0].isocalendar()[1]}",
                orders=row[1],
                revenue=float(row[2]) if row[2] else 0.0,
            )
            for row in weekly_raw
        ]

        # 12-Month Base (sliced for 3-month and yearly views)
        last_12_months = today_start - timedelta(days=365)
        monthly_raw = await TblOrders.get_timeseries_stats(db, "month", last_12_months)
        all_monthly = [
            TimeSeriesData(
                date=row[0].strftime("%b %Y"),
                orders=row[1],
                revenue=float(row[2]) if row[2] else 0.0,
            )
            for row in monthly_raw
        ]

        # User Breakdown
        role_stats = await TblUsers.get_role_stats(db)
        user_roles_counts = {role.value: count for role, count in role_stats if role}

        # Recent Feed
        recent_orders = await TblOrders.get_recent_orders(db, limit=5)

        # Growth Trend Logic
        prev_7_days_start = last_7_days - timedelta(days=7)
        _, prev_7_rev_sum = await TblOrders.get_stats_in_range(
            db, prev_7_days_start, last_7_days
        )
        prev_7_rev = float(prev_7_rev_sum) if prev_7_rev_sum else 0.0
        curr_7_rev = sum(d.revenue for d in daily_stats)

        profit_loss = "Growth" if curr_7_rev >= prev_7_rev else "Loss"

        stats = DashboardStatsResponse(
            restaurants=int(restaurants),
            categories=int(categories),
            food_items=int(food_items),
            users=int(users),
            today_orders=today_orders,
            today_revenue=today_revenue,
            total_revenue=total_revenue,
            total_orders=total_orders,
            status_counts=status_counts,
            user_roles_counts=user_roles_counts,
            daily_stats=daily_stats,
            weekly_stats=weekly_stats,
            monthly_stats=all_monthly[-6:],
            three_month_stats=all_monthly[-3:],
            yearly_stats=all_monthly,
            recent_restaurants=[
                RecentRestaurantSchema(name=r.name, address=r.address, phone=r.phone)
                for r in recent_res
            ],
            recent_users=[
                RecentUserSchema(username=u.username, email=u.email, role=u.role.value)
                for u in recent_usr
            ],
            recent_orders=[
                RecentOrderSchema(
                    uuid=str(o.uuid),
                    amount=o.total_amount,
                    status=o.status.value,
                    created_at=o.created_at,
                )
                for o in recent_orders
            ],
            profit_loss_status=profit_loss,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.LOGIN_SUCCESS, lang, data=stats
        )

    @staticmethod
    async def get_admin_profile(current_admin, lang: str):

        profile = AdminProfileResponse(
            username=current_admin.username,
            email=current_admin.email,
            role=current_admin.role,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.PROFILE_FETCHED, lang, data=profile
        )


class AdminUserService:
    @staticmethod
    async def list_users(
        db: AsyncSession, skip: int, limit: int, role: str | None, lang: str
    ):
        from app.api.admin.schema import PaginatedUserResponse, UserResponseModel
        from app.models.main.users import TblUsers, UserRole

        role_enum = UserRole(role) if role else None
        total, users = await TblUsers.list_users(
            db, skip=skip, limit=limit, role=role_enum
        )

        response_data = PaginatedUserResponse(
            total=total,
            items=[
                UserResponseModel(
                    uuid=u.uuid,
                    username=u.username,
                    email=u.email,
                    role=u.role.value,
                    is_active=u.is_active,
                )
                for u in users
            ],
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USERS_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def get_user(db: AsyncSession, user_uuid: str, lang: str):
        from app.api.admin.schema import UserResponseModel
        from app.models.main.users import TblUsers

        user = await TblUsers.get_by_uuid(user_uuid, db)
        if not user:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        response_data = UserResponseModel(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
        )
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USER_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def update_user(db: AsyncSession, user_uuid: str, req_data: dict, lang: str):
        from app.api.admin.schema import UserResponseModel
        from app.models.main.users import TblUsers

        user = await TblUsers.get_by_uuid(user_uuid, db)
        if not user:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        updated_user = await user.update(db, req_data)

        response_data = UserResponseModel(
            uuid=updated_user.uuid,
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role.value,
            is_active=updated_user.is_active,
        )
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USER_UPDATED, lang, data=response_data
        )

    @staticmethod
    async def delete_user(db: AsyncSession, user_uuid: str, lang: str):
        from app.models.main.users import TblUsers

        user = await TblUsers.get_by_uuid(user_uuid, db)
        if not user:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        await user.delete(db)
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USER_DELETED, lang
        )

    @staticmethod
    async def create_user(db: AsyncSession, req_data: dict, lang: str):
        from app.api.admin.schema import UserResponseModel
        from app.models.main.users import TblUsers, UserRole, UsersBaseModel
        from app.utils.crypto_utils import hash_password

        existing = await TblUsers.get_by_username(req_data["username"], db)
        if existing:
            return ResponseBuilder.build(
                ErrorType.VAL_400_USERNAME_EXISTS, MessageCode.USERNAME_EXISTS, lang
            )

        new_user = UsersBaseModel(
            username=req_data["username"],
            email=req_data["email"],
            hashed_password=hash_password(req_data["password"]),
            is_active=req_data.get("is_active", True),
        )

        user = await TblUsers.create(new_user, db)
        user.role = UserRole(req_data.get("role", "CUSTOMER"))

        await db.commit()
        await db.refresh(user)

        # Decide message code based on role
        msg_code = MessageCode.CUSTOMER_CREATED
        if user.role == UserRole.ADMIN:
            msg_code = MessageCode.ADMIN_CREATED
        elif user.role == UserRole.DELIVERY_PARTNER:
            msg_code = MessageCode.DELIVERY_PARTNER_CREATED

        response_data = UserResponseModel(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED, msg_code, lang, data=response_data
        )
