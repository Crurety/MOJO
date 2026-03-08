from datetime import datetime
from sqlalchemy import BigInteger, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base


@compiles(BigInteger, "sqlite")
def _compile_bigint_sqlite(_type, _compiler, **_kw):
    # SQLite only auto-increments PRIMARY KEY when type is exactly INTEGER.
    return "INTEGER"

Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
