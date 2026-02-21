from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar
from app.core.error.error_types import ErrorType
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")


class CustomModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
        arbitrary_types_allowed=True,
    )


class CustomResponse(CustomModel, Generic[DataT]):
    status: int
    error_type: ErrorType
    message: str
    status_code: int
    data: DataT | None = None