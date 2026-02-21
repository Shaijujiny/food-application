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
        from app.models.main.users import TblUsers, UserRole

        restaurants = await TblRestaurants.active_restaurants_count(db)
        categories = await TblCategories.active_categories_count(db)
        food_items = await TblFoods.active_foods_count(db)
        users = await TblUsers.total_users_count(db)
        recent_res = await TblRestaurants.get_recent(db)
        recent_usr = await TblUsers.get_recent(db, role=UserRole.CUSTOMER)

        stats = DashboardStatsResponse(
            restaurants=int(restaurants),
            categories=int(categories),
            food_items=int(food_items),
            users=int(users),
            growth=18.5,
            total_revenue=12540.50,
            total_orders=150,
            pending_orders=12,
            completed_orders=138,
            recent_restaurants=[
                {"name": r.name, "address": r.address, "phone": r.phone}
                for r in recent_res
            ],
            recent_users=[
                {"username": u.username, "email": u.email} for u in recent_usr
            ],
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
    async def list_users(db: AsyncSession, skip: int, limit: int, role: str | None, lang: str):
        from app.models.main.users import TblUsers, UserRole
        from app.api.admin.schema import PaginatedUserResponse, UserResponseModel

        role_enum = UserRole(role) if role else None
        total, users = await TblUsers.list_users(db, skip=skip, limit=limit, role=role_enum)

        response_data = PaginatedUserResponse(
            total=total,
            items=[UserResponseModel(
                uuid=u.uuid,
                username=u.username,
                email=u.email,
                role=u.role.value,
                is_active=u.is_active
            ) for u in users]
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USERS_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def get_user(db: AsyncSession, user_uuid: str, lang: str):
        from app.models.main.users import TblUsers
        from app.api.admin.schema import UserResponseModel

        user = await TblUsers.get_by_uuid(user_uuid, db)
        if not user:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        response_data = UserResponseModel(
            uuid=user.uuid,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active
        )
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USER_FETCHED, lang, data=response_data
        )

    @staticmethod
    async def update_user(db: AsyncSession, user_uuid: str, req_data: dict, lang: str):
        from app.models.main.users import TblUsers
        from app.api.admin.schema import UserResponseModel

        user = await TblUsers.get_by_uuid(user_uuid, db)
        if not user:
            return ResponseBuilder.build(
                ErrorType.ERR_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        updated_user = await user.update(db, req_data)

        response_data = UserResponseModel(
            uuid=updated_user.uuid,
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role.value,
            is_active=updated_user.is_active
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
                ErrorType.ERR_404_NOT_FOUND, MessageCode.USER_NOT_FOUND, lang
            )

        await user.delete(db)
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.USER_DELETED, lang
        )
