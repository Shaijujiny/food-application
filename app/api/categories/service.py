# app/api/categories/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.main.categories import CategoryBaseModel, TblCategories

from app.core.response.response_builder import ResponseBuilder
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode

from app.api.categories.schema import CategoryCreate, CategoryResponse


class CategoryService:

    @staticmethod
    async def create(
        data: CategoryCreate,
        db: AsyncSession,
        lang: str
    ):

        category = CategoryBaseModel(
            name=data.name,
            restaurant_id=data.restaurant_id
        )

        created = await TblCategories.create(category, db)
        await db.commit()
        await db.refresh(created)

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.CUSTOMER_CREATED,  # You can create CATEGORY_CREATED if needed
            lang,
            data=CategoryResponse.model_validate(created)
        )

    @staticmethod
    async def get_by_restaurant(
        restaurant_id: int,
        db: AsyncSession,
        lang: str
    ):

        result = await db.execute(
            select(TblCategories).where(
                TblCategories.restaurant_id == restaurant_id
            )
        )

        categories = result.scalars().all()

        category_list = [
            CategoryResponse.model_validate(cat)
            for cat in categories
        ]

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.PROFILE_FETCHED,
            lang,
            data=category_list
        )

    @staticmethod
    async def delete(
        cat_id: int,
        db: AsyncSession,
        lang: str
    ):

        result = await db.execute(
            select(TblCategories).where(TblCategories.cat_id == cat_id)
        )

        category = result.scalar_one_or_none()

        if not category:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,  # Better to add CATEGORY_NOT_FOUND
                lang
            )

        await db.delete(category)
        await db.commit()

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang
        )