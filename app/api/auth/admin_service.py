# app/api/auth/admin_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.main.users import TblUsers, UsersBaseModel, UserRole
from app.utils.crypto_utils import hash_password, verify_password
from app.depends.jwt_depends import JWTService

from app.core.response.response_builder import ResponseBuilder
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode

from app.api.auth.schema import RegisterRequest, LoginRequest, TokenData, ProfileResponse


jwt_service = JWTService()


class AdminAuthService:

    @staticmethod
    async def register(
        data: RegisterRequest,
        db: AsyncSession,
        lang: str
    ):

        existing = await TblUsers.get_by_username(data.username, db)

        if existing:
            return ResponseBuilder.build(
                ErrorType.VAL_400_USERNAME_EXISTS,
                MessageCode.USERNAME_EXISTS,
                lang
            )

        new_user = UsersBaseModel(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_active=True
        )

        user = await TblUsers.create(new_user, db)
        user.role = UserRole.ADMIN

        await db.commit()
        await db.refresh(user)

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.ADMIN_CREATED,
            lang,
            data=ProfileResponse.model_validate(user)
        )

    @staticmethod
    async def login(
        data: LoginRequest,
        db: AsyncSession,
        lang: str
    ):

        user = await TblUsers.get_by_username(data.username, db)

        if not user or user.role != UserRole.ADMIN:
            return ResponseBuilder.build(
                ErrorType.AUTH_401_INVALID_CREDENTIALS,
                MessageCode.INVALID_CREDENTIALS,
                lang
            )

        if not verify_password(data.password, user.hashed_password):
            return ResponseBuilder.build(
                ErrorType.AUTH_401_INVALID_CREDENTIALS,
                MessageCode.INVALID_CREDENTIALS,
                lang
            )

        access = await jwt_service.create_access_token(user.uuid, user.role)
        refresh = await jwt_service.create_refresh_token(user.uuid, user.role)

        token_data = TokenData(
            access_token=access,
            refresh_token=refresh
        )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang,
            data=token_data
        )