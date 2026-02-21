# app/api/restaurants/service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.main.restaurants import RestaurantBaseModel, TblRestaurants

from app.core.response.response_builder import ResponseBuilder
from app.core.error.error_types import ErrorType
from app.core.error.message_codes import MessageCode

from app.api.restaurants.schema import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
)


class RestaurantService:

    @staticmethod
    async def create(data: RestaurantCreate, db: AsyncSession, lang: str):

        restaurant = RestaurantBaseModel(
            name=data.name,
            address=data.address,
            phone=data.phone
        )

        created = await TblRestaurants.create(restaurant, db)
        await db.commit()
        await db.refresh(created)

        return ResponseBuilder.build(
            ErrorType.SUC_201_CREATED,
            MessageCode.CUSTOMER_CREATED,  # Better: add RESTAURANT_CREATED
            lang,
            data=RestaurantResponse.model_validate(created)
        )

    @staticmethod
    async def get_all(db: AsyncSession, lang: str):

        result = await db.execute(select(TblRestaurants))
        restaurants = result.scalars().all()

        response_list = [
            RestaurantResponse.model_validate(r)
            for r in restaurants
        ]

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.PROFILE_FETCHED,
            lang,
            data=response_list
        )

    @staticmethod
    async def get_by_uuid(uuid: str, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblRestaurants).where(TblRestaurants.uuid == uuid)
        )

        restaurant = result.scalar_one_or_none()

        if not restaurant:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,  # Better: add RESTAURANT_NOT_FOUND
                lang
            )

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.PROFILE_FETCHED,
            lang,
            data=RestaurantResponse.model_validate(restaurant)
        )

    @staticmethod
    async def update(uuid: str, data: RestaurantUpdate, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblRestaurants).where(TblRestaurants.uuid == uuid)
        )

        restaurant = result.scalar_one_or_none()

        if not restaurant:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,
                lang
            )

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(restaurant, key, value)

        await db.commit()
        await db.refresh(restaurant)

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang,
            data=RestaurantResponse.model_validate(restaurant)
        )

    @staticmethod
    async def delete(uuid: str, db: AsyncSession, lang: str):

        result = await db.execute(
            select(TblRestaurants).where(TblRestaurants.uuid == uuid)
        )

        restaurant = result.scalar_one_or_none()

        if not restaurant:
            return ResponseBuilder.build(
                ErrorType.RES_404_NOT_FOUND,
                MessageCode.INVALID_CREDENTIALS,
                lang
            )

        await db.delete(restaurant)
        await db.commit()

        return ResponseBuilder.build(
            ErrorType.SUC_200_OK,
            MessageCode.LOGIN_SUCCESS,
            lang
        )