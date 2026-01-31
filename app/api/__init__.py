from fastapi import APIRouter
from app.api.utils.router import utils_router
from app.api.users.router import router as users_router

api_router = APIRouter()


api_router.include_router(utils_router)
api_router.include_router(users_router)