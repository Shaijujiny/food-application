from fastapi import APIRouter

from app.api.admin.router import router as admin_router
from app.api.auth.router import router as api
from app.api.categories.router import router as category_router
from app.api.foods.router import router as food_router
from app.api.notifications.router import router as notifications_router
from app.api.orders.router import router as orders_router
from app.api.restaurants.router import router as restaurant_router
from app.api.utils.router import utils_router

api_router = APIRouter()


api_router.include_router(utils_router)
api_router.include_router(api)
api_router.include_router(restaurant_router)
api_router.include_router(category_router)
api_router.include_router(food_router)
api_router.include_router(orders_router)
api_router.include_router(admin_router)
api_router.include_router(notifications_router)
