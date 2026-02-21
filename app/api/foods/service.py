# app/api/foods/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.main.food import FoodSBaseModel, TblFoods

from app.core.response.response_builder import ResponseBuilder
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode

from app.api.foods.schema import FoodCreate, FoodUpdate, FoodResponse


class FoodService:

    @staticmethod
    async def create(data: FoodCreate, db: AsyncSession, lang: str):

        food = FoodSBaseModel(
            name=data.name,
            price=data.price,
            category_id=data.category_id
        )

        created = await TblFoods.create(food, db)
        await db.commit()
        await db.refresh(created)

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.CUSTOMER_CREATED,  # Better: add FOOD_CREATED
            lang,
            data=FoodResponse.model_validate(created)
        )

    @staticmethod
    async def get_by_category(category_id: int, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblFoods).where(TblFoods.category_id == category_id)
        )

        foods = result.scalars().all()

        food_list = [
            FoodResponse.model_validate(food)
            for food in foods
        ]

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.PROFILE_FETCHED,
            lang,
            data=food_list
        )

    @staticmethod
    async def update(food_id: int, data: FoodUpdate, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblFoods).where(TblFoods.food_id == food_id)
        )

        food = result.scalar_one_or_none()

        if not food:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,  # Better: add FOOD_NOT_FOUND
                lang
            )

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(food, key, value)

        await db.commit()
        await db.refresh(food)

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang,
            data=FoodResponse.model_validate(food)
        )

    @staticmethod
    async def delete(food_id: int, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblFoods).where(TblFoods.food_id == food_id)
        )

        food = result.scalar_one_or_none()

        if not food:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,
                lang
            )

        await db.delete(food)
        await db.commit()

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang
        )