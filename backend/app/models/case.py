"""
Database model for a MedRecon reconciliation case.

A case represents one complete medication reconciliation workflow.
It acts as the parent record for source documents, medication events,
agent runs, discrepancies, interaction findings, and human reviews.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CaseStatus(str, Enum):
    """
    Define the lifecycle states of a MedRecon case.

    CREATED:
        The case exists but reconciliation has not started.

    PROCESSING:
        The agent workflow is currently running.

    READY_FOR_REVIEW:
        Automated processing has finished and findings are ready
        for qualified human review.

    COMPLETED:
        The intended reconciliation and review workflow is complete.

    FAILED:
        Processing could not finish successfully.
    """

    CREATED = "created"
    PROCESSING = "processing"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
    FAILED = "failed"


class Case(TimestampMixin, Base):
    """
    Store one MedRecon medication reconciliation workflow.

    Why this exists:
        Every source, extracted medication event, finding, agent run,
        and review needs to belong to one reconciliation case.

    Fields:
        id:
            Internal globally unique identifier.

        external_reference:
            Optional human-readable reference such as SYN-001 or DEMO-001.

        title:
            Short display name for the case.

        status:
            Current workflow state.

    Safety:
        This model stores workflow metadata only. It does not diagnose,
        prescribe, discontinue medication, or determine medication truth.

    Privacy:
        Hackathon evaluation cases should use synthetic identifiers
        rather than real patient identifiers.
    """

    __tablename__ = "cases"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    status: Mapped[CaseStatus] = mapped_column(
        SqlEnum(
            CaseStatus,
            name="case_status",
            native_enum=False,
        ),
        default=CaseStatus.CREATED,
        nullable=False,
    )