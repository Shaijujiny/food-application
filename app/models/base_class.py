

from typing import Any, Dict

from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative


"""Lightweight declarative base used by the project's models.

This module intentionally keeps the Base minimal and portable:
- Removes unused MySQL-specific constants
- Exposes a declarative Base with a PostgreSQL-friendly naming convention

Models should simply inherit from `Base`.
"""


# PostgreSQL-friendly naming convention for indexes/constraints
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_label)s",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class_registry: Dict[str, Any] = {}


@as_declarative(class_registry=class_registry)
class Base:
    """Base class for SQLAlchemy models used across the project.

    Intended usage:
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)

    The `metadata` attribute below ensures the naming convention is applied
    for created constraints (helpful when targeting PostgreSQL).
    """

    # Basic annotations that code elsewhere in the project may rely on
    record_id: Any
    class_name: str

    __abstract__: bool = True

    # Apply the PostgreSQL-friendly naming convention to metadata
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        pk = getattr(self, "id", getattr(self, "record_id", None))
        return f"<{self.__class__.__name__} id={pk!r}>"

