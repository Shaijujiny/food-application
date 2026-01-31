from fastapi import APIRouter, Depends

from app.api.users.schema import UserRegister
from app.api.users.service import UserService
from app.database.postgresql import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/users/me")
async def read_current_user(db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_all_user()

@router.post("/users/register")
async def register_user(user_data : UserRegister , db: AsyncSession = Depends(get_db)):

    return await UserService(db).register_user(user_data)