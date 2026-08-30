"""
Shared SQLAlchemy model foundation for MedRecon AI.

This module defines the declarative base used by all database models
and reusable timestamp fields for records that need creation and
modification tracking.

Keeping this logic in one place makes the database layer consistent
and easier to maintain.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Consistent database constraint names make migrations easier to read,
# debug, and reproduce across development and production databases.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": (
        "fk_%(table_name)s_%(column_0_name)s_"
        "%(referred_table_name)s"
    ),
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for every SQLAlchemy database model in MedRecon AI.

    Why this exists:
        SQLAlchemy needs a shared declarative base so that it can
        discover database tables and their relationships.

    Usage:
        Database models should inherit from this class.

        Example:
            class Case(Base):
                ...

    Safety:
        This class contains no patient information and performs no
        clinical reasoning. It only provides database metadata.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """
    Add creation and modification timestamps to database models.

    Why this exists:
        MedRecon AI needs traceability. Records such as cases,
        medication events, findings, and reviews should record when
        they were created and last modified.

    Fields:
        created_at:
            UTC timestamp generated when the record is created.

        updated_at:
            UTC timestamp generated when the record is created and
            refreshed whenever the record is updated.

    Safety:
        These timestamps support auditing but should not be interpreted
        as clinical event timestamps. Clinical event dates will be
        stored separately on medication-event records.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )