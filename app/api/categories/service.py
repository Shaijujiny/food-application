# app/api/categories/service.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.categories.schema import CategoryCreate, CategoryResponse, CategoryUpdate
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode
from app.core.response.response_builder import ResponseBuilder
from app.models.main.categories import CategoryBaseModel, TblCategories


class CategoryService:
    @staticmethod
    async def create(data: CategoryCreate, db: AsyncSession, lang: str):

        # Use the full data model; description is now part of CategoryBaseModel
        category = CategoryBaseModel(
            name=data.name,
            restaurant_id=data.restaurant_id,
            image_data=data.image_data,
            description=getattr(data, "description", None),
        )

        created = await TblCategories.create(category, db)
        await db.commit()
        await db.refresh(created)

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.CUSTOMER_CREATED,  # You can create CATEGORY_CREATED if needed
            lang,
            data=CategoryResponse.model_validate(created),
        )

    @staticmethod
    async def get_by_restaurant(restaurant_id: int, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblCategories).where(TblCategories.restaurant_id == restaurant_id)
        )

        categories = result.scalars().all()

        category_list = [CategoryResponse.model_validate(cat) for cat in categories]

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.PROFILE_FETCHED, lang, data=category_list
        )

    @staticmethod
    async def get_all(db: AsyncSession, lang: str):
        """Return all categories (admin only)"""
        result = await db.execute(select(TblCategories))
        categories = result.scalars().all()
        category_list = [CategoryResponse.model_validate(cat) for cat in categories]
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.PROFILE_FETCHED, lang, data=category_list
        )

    @staticmethod
    async def delete(cat_id: int, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblCategories).where(TblCategories.cat_id == cat_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,  # Better to add CATEGORY_NOT_FOUND
                lang,
            )
        await db.delete(category)
        await db.commit()
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK, MessageCode.LOGIN_SUCCESS, lang
        )

    @staticmethod
    async def update(cat_id: int, data: CategoryUpdate, db: AsyncSession, lang: str):
        """Update a category's fields (admin only)."""
        result = await db.execute(
            select(TblCategories).where(TblCategories.cat_id == cat_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,  # Better to add CATEGORY_NOT_FOUND
                lang,
            )
        # Apply updates if provided
        if data.name is not None:
            category.name = data.name
        if data.image_data is not None:
            category.image_data = data.image_data
        if getattr(data, "description", None) is not None:
            category.description = data.description
        await db.flush()
        await db.commit()
        # Return updated representation
        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang,
            data=CategoryResponse.model_validate(category),
        )
