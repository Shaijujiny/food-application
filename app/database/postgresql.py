"""Async PostgreSQL helper using SQLAlchemy AsyncEngine."""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, List

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import inspect

from app.config import CONFIG_SETTINGS
from app.models.base_class import Base


_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_database_url() -> str:
    user = CONFIG_SETTINGS.POSTGRESQL_DB_USER
    password = CONFIG_SETTINGS.POSTGRESQL_DB_PASSWORD
    host = CONFIG_SETTINGS.POSTGRESQL_DB_HOST or "localhost"
    port = CONFIG_SETTINGS.POSTGRESQL_DB_PORT or 5432
    db = CONFIG_SETTINGS.POSTGRESQL_DB_NAME or "postgres"

    connection= f"postgresql+asyncpg://shaijujin:shaiju123@127.0.0.1:5432/food"
    print("connection configured successfully : ", connection)
    return connection


def init_engine(echo: bool = False) -> AsyncEngine:
    global _engine, _session_maker

    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=echo,
            pool_pre_ping=True,
        )
        _session_maker = async_sessionmaker(
            _engine, expire_on_commit=False
        )

    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    if _session_maker is None:
        init_engine()
    return _session_maker  # type: ignore[return-value]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def create_tables_and_get_names() -> List[str]:
    """
    Create tables if not exists and return table names.
    """
    # Ensure models are imported
    import app.models.main.users  # noqa: F401

    engine = init_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )


def create_tables_sync_blocking() -> None:
    try:
        asyncio.run(create_tables_and_get_names())
    except Exception as exc:
        raise RuntimeError(f"Failed creating tables: {exc}") from exc
