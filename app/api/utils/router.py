from fastapi import APIRouter

from app.database.postgresql import create_tables_and_get_names
from app.utils.schemas_utils import CustomResponse

utils_router = APIRouter()


@utils_router.get("/init-db", tags=["Utils:Database"])
async def init_db() -> CustomResponse:
    """Initialize the database by creating all tables defined in the models."""
    await create_tables_and_get_names()
    return CustomResponse(
        status="1",
        status_code=200,
        message="Database initialized successfully",
    )


@utils_router.get("/run-migration", tags=["Utils:Database"])
async def run_migration() -> CustomResponse:
    """Run manual database migrations like adding new columns."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    import app.models.main.notifications  # noqa: F401
    import app.models.main.orders  # noqa: F401
    from app.database.postgresql import get_database_url
    from app.models.base_class import Base

    engine = create_async_engine(get_database_url())
    messages = []

    # 1. Add cat_image
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text("ALTER TABLE public.tbl_categories ADD COLUMN cat_image TEXT;")
            )
            messages.append("Added cat_image to tbl_categories")
        except Exception as e:
            messages.append(f"cat_image skip (exists?): {str(e)[:50]}")

    # 1b. Add cat_description
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text(
                    "ALTER TABLE public.tbl_categories ADD COLUMN cat_description TEXT;"
                )
            )
            messages.append("Added cat_description to tbl_categories")
        except Exception as e:
            messages.append(f"cat_description skip (exists?): {str(e)[:50]}")

    # 2. Add food_image
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text("ALTER TABLE public.tbl_foods ADD COLUMN food_image TEXT;")
            )
            messages.append("Added food_image to tbl_foods")
        except Exception as e:
            messages.append(f"food_image skip (exists?): {str(e)[:50]}")

    # 3. Add res_email
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text(
                    "ALTER TABLE public.tbl_restaurants ADD COLUMN res_email VARCHAR(255);"
                )
            )
            messages.append("Added res_email to tbl_restaurants")
        except Exception as e:
            messages.append(f"res_email skip: {str(e)[:50]}")

    # 4. Add notif_related_user_id
    async with engine.begin() as conn:
        try:
            await conn.execute(
                text(
                    "ALTER TABLE public.tbl_notifications ADD COLUMN notif_related_user_id INTEGER REFERENCES public.tbl_users(usr_id) ON DELETE CASCADE;"
                )
            )
            messages.append("Added notif_related_user_id to tbl_notifications")
        except Exception as e:
            messages.append(f"notif_related_user_id skip: {str(e)[:50]}")

    # 5. Ensure all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        messages.append("Ensured all missing tables are created")

    return CustomResponse(
        status="1",
        status_code=200,
        message="Migration completed successfully",
        data={"details": messages},
    )
