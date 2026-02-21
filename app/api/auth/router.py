# app/api/auth/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_db
from app.depends.language_depends import get_language

from app.core.response.base_schema import CustomResponse
from app.api.auth.schema import (
    RegisterRequest,
    LoginRequest,
    TokenData,
    ProfileResponse,
)

from app.api.auth.customer_service import CustomerAuthService
from app.api.auth.admin_service import AdminAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/customer/register",
    response_model=CustomResponse[ProfileResponse]
)
async def register_customer(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await CustomerAuthService.register(data, db, lang)


@router.post(
    "/customer/login",
    response_model=CustomResponse[TokenData]
)
async def customer_login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await CustomerAuthService.login(data, db, lang)


@router.post(
    "/admin/register",
    response_model=CustomResponse[ProfileResponse]
)
async def register_admin(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await AdminAuthService.register(data, db, lang)


@router.post(
    "/admin/login",
    response_model=CustomResponse[TokenData]
)
async def admin_login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await AdminAuthService.login(data, db, lang)