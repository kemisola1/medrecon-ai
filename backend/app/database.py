"""
Database connection and session management for MedRecon AI.

This module creates the SQLAlchemy database engine and provides
database sessions to the rest of the application.

The database URL comes from application settings, which allows
MedRecon AI to use SQLite during local development and PostgreSQL
or another supported database in deployment.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


# SQLite requires this option when the same database connection may be
# accessed across multiple threads, such as during FastAPI requests or tests.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for a single application operation.

    Why this exists:
        FastAPI endpoints and backend services need a safe, consistent
        way to access the database.

    Yields:
        An active SQLAlchemy Session.

    Cleanup:
        The session is always closed after the request or operation
        finishes, even when an exception occurs.

    Safety:
        Closing sessions reliably prevents connection leaks and avoids
        unintended sharing of database state between requests.

    Failure behavior:
        Database exceptions are allowed to propagate to the calling
        layer, where they can be logged and handled appropriately.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()