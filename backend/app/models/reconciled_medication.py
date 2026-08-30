"""
Database model for reconciled medication states in MedRecon AI.

A ReconciledMedication represents the best-supported medication state
produced after reviewing multiple medication events, chronology, and
supporting evidence.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ReconciliationStatus(str, Enum):
    """
    Allowed reconciled medication states.

    CURRENT:
        Best available evidence supports that the medication is current.

    RECENTLY_ADDED:
        Evidence supports that the medication was added recently.

    DISCONTINUED:
        Best available evidence supports that the medication was stopped.

    CHANGED:
        A meaningful dose, frequency, route, or regimen change was detected.

    CONFLICTING:
        Available evidence contains unresolved conflicting information.

    UNCERTAIN:
        Evidence is incomplete or insufficient to determine the state
        confidently.
    """

    CURRENT = "current"
    RECENTLY_ADDED = "recently_added"
    DISCONTINUED = "discontinued"
    CHANGED = "changed"
    CONFLICTING = "conflicting"
    UNCERTAIN = "uncertain"


class ReconciledMedication(TimestampMixin, Base):
    """
    Store the best-supported medication state for a reconciliation case.

    Why this exists:
        MedRecon AI needs a structured output that summarizes the
        medication picture after timeline reconstruction and
        reconciliation.

    Fields:
        id:
            Internal unique identifier.

        case_id:
            Reconciliation case this medication belongs to.

        medication_name:
            Human-readable medication name.

        normalized_medication_id:
            Optional normalized medication identifier.

        dose:
            Best-supported dose when available.

        frequency:
            Best-supported administration frequency when available.

        route:
            Best-supported route when available.

        status:
            Reconciliation result for this medication.

        confidence:
            Confidence score from 0.0 to 1.0 when available.

        requires_human_review:
            Indicates whether qualified human review is required.

    Safety:
        This record represents a best-supported reconciliation result,
        not absolute confirmation of what a patient is physically taking.

        It must never be interpreted as authorization to prescribe,
        discontinue, or modify medication therapy.

    Uncertainty:
        Conflicting or insufficient evidence should result in
        CONFLICTING or UNCERTAIN states rather than unsupported guesses.
    """

    __tablename__ = "reconciled_medications"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    medication_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_medication_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    dose: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    frequency: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    route: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[ReconciliationStatus] = mapped_column(
        SqlEnum(
            ReconciliationStatus,
            name="reconciliation_status",
            native_enum=False,
        ),
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    requires_human_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )