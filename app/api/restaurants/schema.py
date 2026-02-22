# app/api/restaurants/schema.py

from app.core.response.base_schema import CustomModel

# ================= REQUEST =================


class RestaurantCreate(CustomModel):
    name: str
    address: str
    phone: str
    email: str | None = None


class RestaurantUpdate(CustomModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


# ================= RESPONSE =================


class RestaurantResponse(CustomModel):
    res_id: int
    uuid: str
    name: str
    address: str
    phone: str
    email: str | None = None
    is_active: bool
