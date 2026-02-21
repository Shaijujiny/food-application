# app/api/categories/schema.py

from app.core.response.base_schema import CustomModel


# ================= REQUEST =================

class CategoryCreate(CustomModel):
    name: str
    restaurant_id: int


class CategoryUpdate(CustomModel):
    name: str | None = None


# ================= RESPONSE =================

class CategoryResponse(CustomModel):
    cat_id: int
    name: str
    restaurant_id: int