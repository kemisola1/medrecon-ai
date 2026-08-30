"""
Database initialization utilities for MedRecon AI.

This module creates database tables from the SQLAlchemy models
registered with the shared Base metadata.
"""

from app.database import engine
from app.models.base import Base
from app.models.case import Case  # noqa: F401
from app.models.source import Source  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.medication_event import MedicationEvent  # noqa: F401
from app.models.reconciled_medication import ReconciledMedication  # noqa: F401
from app.models.discrepancy import Discrepancy  # noqa: F401
from app.models.interaction import InteractionFinding  # noqa: F401
from app.models.agent_run import AgentRun, AgentStep  # noqa: F401
from app.models.human_review import HumanReview  # noqa: F401




def init_db() -> None:
    """
    Create all currently registered MedRecon database tables.

    Why this exists:
        SQLAlchemy only creates tables for models that have been
        imported and registered with Base.metadata.

    Inputs:
        None.

    Returns:
        None.

    Safety:
        This function only creates missing database tables.
        It does not perform clinical reasoning or modify medication
        decisions.

    Limitation:
        This is appropriate for early development. Later, Alembic
        migrations will manage schema changes more safely.
    """

    Base.metadata.create_all(bind=engine)