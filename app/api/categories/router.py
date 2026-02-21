# app/api/categories/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

from app.api.categories.service import CategoryService
from app.api.categories.schema import CategoryCreate

router = APIRouter(prefix="/categories", tags=["Categories"])


# 🔐 ADMIN ONLY
@router.post("/")
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await CategoryService.create(data, db, lang)


# 👤 Public (or can restrict if needed)
@router.get("/restaurant/{restaurant_id}")
async def get_categories(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await CategoryService.get_by_restaurant(restaurant_id, db, lang)


# 🔐 ADMIN ONLY
@router.delete("/{cat_id}")
async def delete_category(
    cat_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await CategoryService.delete(cat_id, db, lang)