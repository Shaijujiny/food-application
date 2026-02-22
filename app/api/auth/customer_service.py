# app/api/auth/customer_service.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.schema import (
    LoginRequest,
    ProfileResponse,
    RegisterRequest,
    TokenData,
)
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.response_builder import ResponseBuilder
from app.depends.jwt_depends import JWTService
from app.models.main.users import TblUsers, UserRole, UsersBaseModel
from app.utils.crypto_utils import hash_password, verify_password

jwt_service = JWTService()


class CustomerAuthService:
    @staticmethod
    async def register(data: RegisterRequest, db: AsyncSession, lang: str):

        existing = await TblUsers.get_by_username(data.username, db)

        if existing:
            return ResponseBuilder.build(
                ErrorType.VAL_400_USERNAME_EXISTS, MessageCode.USERNAME_EXISTS, lang
            )

        new_user = UsersBaseModel(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=True,
        )

        user = await TblUsers.create(new_user, db)
        user.role = UserRole.CUSTOMER

        await db.commit()
        await db.refresh(user)

        # Notify Admin
        from app.api.notifications.service import NotificationService
        from app.models.main.notifications import NotificationType

        await NotificationService.create_system_notification(
            db=db,
            title="New User Registration",
            message=f"New customer registered: {user.username} ({user.email})",
            type=NotificationType.NEW_USER,
            user_id=None,
            related_user_id=user.usr_id,
        )

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.CUSTOMER_CREATED,
            lang,
            data=ProfileResponse.model_validate(user),
        )

    @staticmethod
    async def login(data: LoginRequest, db: AsyncSession, lang: str):

        user = await TblUsers.get_by_username(data.username, db)

        if not user or not verify_password(data.password, user.hashed_password):
            return ResponseBuilder.build(
                ErrorType.AUTH_401_INVALID_CREDENTIALS,
                MessageCode.INVALID_CREDENTIALS,
                lang,
            )

        access = await jwt_service.create_access_token(user.uuid, user.role)
        refresh = await jwt_service.create_refresh_token(user.uuid, user.role)

        token_data = TokenData(access_token=access, refresh_token=refresh)

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.LOGIN_SUCCESS, lang, data=token_data
        )
