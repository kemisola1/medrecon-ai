"""
Tests for the MedRecon Case database model.

These tests confirm that a Case can be created, stored, and retrieved
using SQLAlchemy.
"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.base import Base
from app.models.case import Case, CaseStatus


def test_create_and_retrieve_case() -> None:
    """
    Confirm that a MedRecon Case can be persisted and retrieved.

    Why this test exists:
        The application depends on Case records as the parent object
        for reconciliation workflows. We need confidence that the model
        behaves correctly before adding more related tables.

    Safety:
        This test uses only synthetic data and an in-memory SQLite
        database. No real patient information is involved.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        case = Case(
            external_reference="SYN-001",
            title="Synthetic Medication Reconciliation Case",
        )

        session.add(case)
        session.commit()

        statement = select(Case).where(
            Case.external_reference == "SYN-001"
        )

        saved_case = session.scalar(statement)

        assert saved_case is not None
        assert saved_case.title == (
            "Synthetic Medication Reconciliation Case"
        )
        assert saved_case.status == CaseStatus.CREATED