# app/api/categories/routes.py

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.categories.schema import CategoryCreate, CategoryResponse
from app.api.categories.service import CategoryService
from app.core.response.base_schema import CustomResponse
from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

router = APIRouter(prefix="/categories", tags=["Categories"])


# 🔐 ADMIN ONLY
@router.post("/")
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    return await CategoryService.create(data, db, lang)


# 🔐 ADMIN ONLY - List all categories
@router.get("/", response_model=CustomResponse[List[CategoryResponse]])
async def get_all_categories(
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    return await CategoryService.get_all(db, lang)


# 👤 Public (or can restrict if needed)
@router.get("/restaurant/{restaurant_id}")
async def get_categories(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    return await CategoryService.get_by_restaurant(restaurant_id, db, lang)


# 🔐 ADMIN ONLY
@router.delete("/{cat_id}")
async def delete_category(
    cat_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language),
):
    return await CategoryService.delete(cat_id, db, lang)
