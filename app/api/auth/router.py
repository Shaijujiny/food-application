# app/api/auth/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.admin_service import AdminAuthService
from app.api.auth.customer_service import CustomerAuthService
from app.api.auth.schema import (
    LoginRequest,
    ProfileResponse,
    RegisterRequest,
    TokenData,
)
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.base_schema import CustomResponse
from app.core.response.response_builder import ResponseBuilder
from app.database.postgresql import get_db
from app.depends.language_depends import get_language

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/customer/register", response_model=CustomResponse[ProfileResponse])
async def register_customer(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    return await CustomerAuthService.register(data, db, lang)


@router.post("/customer/login", response_model=CustomResponse[TokenData])
async def customer_login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    return await CustomerAuthService.login(data, db, lang)


@router.post("/admin/register", response_model=CustomResponse[ProfileResponse])
async def register_admin(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    return await AdminAuthService.register(data, db, lang)


@router.post("/admin/login", response_model=CustomResponse[TokenData])
async def admin_login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    return await AdminAuthService.login(data, db, lang)


@router.post("/logout")
async def logout(lang: str = Depends(get_language)):
    return ResponseBuilder.build(
        ErrorType.SUC_200_OK,
        MessageCode.LOGIN_SUCCESS,
        lang,
    )
