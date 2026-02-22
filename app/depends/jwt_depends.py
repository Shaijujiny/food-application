import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import CONFIG_SETTINGS
from app.database.postgresql import get_db
from app.models.main.users import TblUsers
from app.utils.schemas_utils import CustomHTTPException, JWTPayloadSchema


class JWTService:
    def __init__(self):
        self.redis = Redis(
            host=CONFIG_SETTINGS.REDIS_DB_HOST,
            port=CONFIG_SETTINGS.REDIS_PORT,
            db=CONFIG_SETTINGS.REDIS_DB,
            password=CONFIG_SETTINGS.REDIS_PASS,
            decode_responses=True,
        )
        self.private_key = CONFIG_SETTINGS.APP_JWT_PRIVATE_KEY.replace("\\n", "\n")
        self.public_key = CONFIG_SETTINGS.APP_JWT_PUBLIC_KEY.replace("\\n", "\n")
        self.issuer = CONFIG_SETTINGS.PROJECT_NAME
        self.audience = "api"

    def _now(self):
        return datetime.now(timezone.utc)

    def _generate_payload(self, request_uuid: str, expire_minutes: int, role: str):
        jti = uuid.uuid4().hex
        expire = self._now() + timedelta(minutes=expire_minutes)

        return {
            "uuid": request_uuid,
            "role": role,
            "iss": self.issuer,
            "aud": self.audience,
            "iat": int(self._now().timestamp()),
            "exp": int(expire.timestamp()),
            "jti": jti,
        }

    # ===============================
    # CREATE ACCESS TOKEN
    # ===============================
    async def create_access_token(self, uuid: str, role: str) -> str:

        payload = self._generate_payload(
            uuid, CONFIG_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES, role
        )

        token = jwt.encode(payload, self.private_key, algorithm="RS256")

        # Store active token
        await self.redis.setex(
            f"access:{uuid}",
            CONFIG_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            token,
        )

        # Store JTI
        await self.redis.setex(
            f"jti:{payload['jti']}",
            CONFIG_SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            uuid,
        )

        return token

    # ===============================
    # CREATE REFRESH TOKEN
    # ===============================
    async def create_refresh_token(self, uuid: str, role: str) -> str:

        payload = self._generate_payload(
            uuid, CONFIG_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES, role
        )

        token = jwt.encode(payload, self.private_key, algorithm="RS256")

        await self.redis.setex(
            f"refresh:{uuid}",
            CONFIG_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            token,
        )

        await self.redis.setex(
            f"refresh_jti:{payload['jti']}",
            CONFIG_SETTINGS.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            uuid,
        )

        return token

    # ===============================
    # VERIFY ACCESS TOKEN
    # ===============================
    async def verify_access_token(self, token: str) -> JWTPayloadSchema:

        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
            )
        except jwt.PyJWTError:
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid or expired token",
            )

        # Check if active token
        stored = await self.redis.get(f"access:{payload['uuid']}")
        if stored != token:
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token revoked",
            )

        # Check JTI
        jti = await self.redis.get(f"jti:{payload['jti']}")
        if not jti:
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token replay detected",
            )
        print("payload configured successfully : ", payload)

        return JWTPayloadSchema(**payload)

    # ===============================
    # VERIFY REFRESH TOKEN
    # ===============================
    async def verify_refresh_token(self, token: str) -> JWTPayloadSchema:

        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
            )
        except jwt.PyJWTError:
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid refresh token",
            )

        stored = await self.redis.get(f"refresh:{payload['uuid']}")
        if stored != token:
            raise CustomHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Refresh token revoked",
            )

        return JWTPayloadSchema(**payload)

    # ===============================
    # REVOKE USER TOKENS
    # ===============================
    async def revoke_user(self, uuid: str):

        await self.redis.delete(f"access:{uuid}")
        await self.redis.delete(f"refresh:{uuid}")


security = HTTPBearer()
jwt_service = JWTService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract and validate access token.
    Return full user object.
    """

    token = credentials.credentials

    # 1️⃣ Verify JWT (signature, exp, redis session, jti)
    payload = await jwt_service.verify_access_token(token)

    # 2️⃣ Fetch user from DB
    user = await TblUsers.get_by_id(payload.uuid, db)

    if not user:
        raise CustomHTTPException(status_code=401, message="User not found")

    if not user.is_active:
        raise CustomHTTPException(status_code=403, message="Inactive user")

    return user


async def get_current_admin_user(current_user=Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise CustomHTTPException(status_code=403, message="Admin access required")
    return current_user


async def get_current_customer_user(current_user=Depends(get_current_user)):
    if current_user.role != "CUSTOMER":
        raise CustomHTTPException(status_code=403, message="Customer access required")
    return current_user
