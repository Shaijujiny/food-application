

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from fastapi import HTTPException, status

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

class JWTPayloadSchema(CustomModel):
    """JWT Payload Schema."""


    uuid: str
    role: str


class CustomHTTPException(HTTPException):

    def __init__(
        self,
        status: str = "-1",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: Optional[str] = None,
        message: str = "Something went wrong",
    ):
        self.status = status
        self.code = code

        super().__init__(
            status_code=status_code,
            detail={
                "status": status,
                "code": code,
                "message": message,
            },
        )