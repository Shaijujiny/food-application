

from app.utils.schemas_utils import CustomModel


class UserRegister(CustomModel):
    """Schema for user registration."""

    email: str
    username: str
    hashed_password: str 