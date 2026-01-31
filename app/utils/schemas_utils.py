

from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CustomModel(BaseModel):
    """Base model for all models in the application."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True,
    )


DataT = TypeVar("DataT")

class CustomResponse(CustomModel, Generic[DataT]):
    """Custom response model for the API."""

    status: str = Field(..., examples=["1", "-1"])
    status_code: int = Field(...,examples=["200","201"])
    message: str = Field(..., examples=["Message", "User already exists"])
    data: DataT | None = None