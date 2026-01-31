

from fastapi import FastAPI
from app.api import api_router
from app.config import CONFIG_SETTINGS
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # perform startup actions here
    try:
        yield
    finally:
        # perform shutdown actions here
        pass


app = FastAPI(
    title=CONFIG_SETTINGS.APP_NAME,
    version=CONFIG_SETTINGS.API_VERSION,
    description=CONFIG_SETTINGS.DESCRIPTION,
    docs_url="/docs" if CONFIG_SETTINGS.IS_SWAGGER_ENABLED else None,
    redoc_url="/redoc" if CONFIG_SETTINGS.IS_SWAGGER_ENABLED else None,
    openapi_url="/openapi.json" if CONFIG_SETTINGS.IS_SWAGGER_ENABLED else None,
    lifespan=lifespan,
    debug=CONFIG_SETTINGS.FASTAPI_DEBUG,
    root_path=CONFIG_SETTINGS.ROOT_PATH,
)


app.include_router(api_router)