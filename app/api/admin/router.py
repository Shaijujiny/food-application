# app/api/admin/routes.py

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.admin.schema import UpdateUserRequestModel
from app.api.admin.service import AdminUserService, DashboardService
from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/dashboard/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    return await DashboardService.get_dashboard_stats(db, lang)


@router.get("/profile")
async def admin_profile(
    current_admin=Depends(get_current_admin_user), lang: str = Depends(get_language)
):
    return await DashboardService.get_admin_profile(current_admin, lang)


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    List users with pagination and role filtering.
    """
    return await AdminUserService.list_users(db, skip, limit, role, lang)


@router.get("/users/{user_uuid}")
async def get_user(
    user_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Get a specific user by UUID.
    """
    return await AdminUserService.get_user(db, user_uuid, lang)


@router.put("/users/{user_uuid}")
async def update_user(
    user_uuid: str,
    req_data: UpdateUserRequestModel,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Update a specific user details.
    """
    return await AdminUserService.update_user(
        db, user_uuid, req_data.model_dump(exclude_unset=True), lang
    )


@router.delete("/users/{user_uuid}")
async def delete_user(
    user_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    """
    Delete a specific user.
    """
    return await AdminUserService.delete_user(db, user_uuid, lang)
