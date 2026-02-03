from __future__ import annotations
import os
import urllib.parse
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_ENGINE = None
_SESSION_FACTORY = None


class Base(DeclarativeBase):
    pass


def _get_connection_string() -> Optional[str]:
    return os.environ.get("AZURE_SQL_CONNECTION_STRING")


def init_engine() -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        return

    conn_str = _get_connection_string()
    if not conn_str:
        return

    odbc_connect = urllib.parse.quote_plus(conn_str)
    url = f"mssql+pyodbc:///?odbc_connect={odbc_connect}"
    _ENGINE = create_engine(url, pool_pre_ping=True)
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)


def get_session_factory():
    if _SESSION_FACTORY is None:
        init_engine()
    return _SESSION_FACTORY


def get_engine():
    if _ENGINE is None:
        init_engine()
    return _ENGINE
