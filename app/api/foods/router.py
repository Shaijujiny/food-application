# app/api/foods/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

from app.api.foods.service import FoodService
from app.api.foods.schema import FoodCreate, FoodUpdate

router = APIRouter(prefix="/foods", tags=["Foods"])


# 🔐 ADMIN ONLY
@router.post("/")
async def create_food(
    data: FoodCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await FoodService.create(data, db, lang)


# 👤 Public
@router.get("/category/{category_id}")
async def get_foods(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await FoodService.get_by_category(category_id, db, lang)


# 🔐 ADMIN ONLY
@router.put("/{food_id}")
async def update_food(
    food_id: int,
    data: FoodUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await FoodService.update(food_id, data, db, lang)


# 🔐 ADMIN ONLY
@router.delete("/{food_id}")
async def delete_food(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await FoodService.delete(food_id, db, lang)