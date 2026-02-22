# app/api/foods/schema.py

from app.core.response.base_schema import CustomModel

# ================= REQUEST =================


class FoodCreate(CustomModel):
    name: str
    price: float
    category_id: int
    image_data: str | None = None


class FoodUpdate(CustomModel):
    name: str | None = None
    price: float | None = None
    is_available: bool | None = None
    image_data: str | None = None


# ================= RESPONSE =================


class FoodResponse(CustomModel):
    food_id: int
    name: str
    price: float
    category_id: int
    is_available: bool
    image_data: str | None = None
