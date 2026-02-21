# app/api/restaurants/routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_db
from app.depends.jwt_depends import get_current_admin_user
from app.depends.language_depends import get_language

from app.api.restaurants.service import RestaurantService
from app.api.restaurants.schema import RestaurantCreate, RestaurantUpdate

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


# 🔐 ADMIN ONLY
@router.post("/")
async def create_restaurant(
    data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await RestaurantService.create(data, db, lang)


# 👤 PUBLIC
@router.get("/")
async def list_restaurants(
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await RestaurantService.get_all(db, lang)


@router.get("/{uuid}")
async def get_restaurant(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language)
):
    return await RestaurantService.get_by_uuid(uuid, db, lang)


# 🔐 ADMIN ONLY
@router.put("/{uuid}")
async def update_restaurant(
    uuid: str,
    data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await RestaurantService.update(uuid, data, db, lang)


# 🔐 ADMIN ONLY
@router.delete("/{uuid}")
async def delete_restaurant(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
    lang: str = Depends(get_language)
):
    return await RestaurantService.delete(uuid, db, lang)