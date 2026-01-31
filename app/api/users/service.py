

from app.api.users.schema import UserRegister
from app.models.main.users import TblUsers, UsersBaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.utils.schemas_utils import CustomResponse


class UserService:
    """Service for user-related DB operations.

    Notes:
    - Expects an AsyncSession instance to be passed in (FastAPI dependency).
    - __init__ is synchronous; async work happens in async methods.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> CustomResponse:
        """Register a new user in the database using AsyncSession.

        Correct sequence:
        - create SQLAlchemy TblUsers instance
        - add to session
        - optionally flush to get defaults populated
        - commit and refresh
        """

        new_user = UsersBaseModel.model_validate(user_data)

        # Add and commit using the async session
        await TblUsers.create(new_user, self.db)
        await self.db.commit()
        # await self.db.refresh(new_user)

        return CustomResponse(status="1", status_code=201, message="User registered successfully")

    async def get_all_user(self):
        stmt = select(TblUsers)
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        return users

