from fastapi import APIRouter

from app.utils.schemas_utils import CustomResponse
from app.database.postgresql import create_tables_and_get_names

utils_router = APIRouter()


@utils_router.get("/init-db", tags=["Utils:Database"])
async def init_db() -> CustomResponse:
    """Initialize the database by creating all tables defined in the models."""
    await create_tables_and_get_names()
    return CustomResponse(status="1",status_code=200,message="Database initialized successfully",)