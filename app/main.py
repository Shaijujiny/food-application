

from fastapi import FastAPI
from app.api import api_router
from app.config import CONFIG_SETTINGS
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    
    allow_credentials=True,
    allow_methods=["*"],            # IMPORTANT
    allow_headers=["*"],
)
app.include_router(api_router)