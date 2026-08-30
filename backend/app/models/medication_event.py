"""
Database model for medication events in MedRecon AI.

A MedicationEvent represents one medication-related observation or
change extracted from a source at a particular point in time.

Events preserve source evidence so that later agents can reconstruct
the medication timeline without losing provenance.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MedicationStatus(str, Enum):
    """
    Status stated or observed in the source.

    ACTIVE:
        The source indicates that the medication is active.

    DISCONTINUED:
        The source indicates that the medication was stopped.

    HELD:
        The medication is temporarily withheld.

    UNKNOWN:
        The source does not provide enough information to determine
        medication status.
    """

    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    HELD = "held"
    UNKNOWN = "unknown"


class MedicationEventType(str, Enum):
    """
    Type of medication event represented by the source information.
    """

    PRESCRIBED = "prescribed"
    STARTED = "started"
    CONTINUED = "continued"
    STOPPED = "stopped"
    DOSE_CHANGED = "dose_changed"
    FREQUENCY_CHANGED = "frequency_changed"
    ROUTE_CHANGED = "route_changed"
    REPORTED = "reported"


class MedicationEvent(TimestampMixin, Base):
    """
    Store one medication observation or medication-change event.

    Why this exists:
        Medication reconciliation depends on chronology. Rather than
        immediately overwriting medication information, MedRecon stores
        individual observations as events and later reconstructs the
        best-supported medication state.

    Fields:
        id:
            Internal unique event identifier.

        case_id:
            MedRecon reconciliation case this event belongs to.

        source_id:
            Source from which the event was extracted.

        evidence_id:
            Evidence excerpt supporting the extracted event.

        medication_name:
            Medication name exactly or approximately as extracted.

        normalized_medication_id:
            Optional normalized identifier added by the Medication
            Identity Agent.

        dose:
            Extracted dose when available.

        frequency:
            Extracted frequency when available.

        route:
            Extracted administration route when available.

        status:
            Medication status described by the source.

        event_type:
            Type of medication-related event.

        event_date:
            Clinical/source-related date when known.

        extraction_confidence:
            Confidence in the extraction process from 0.0 to 1.0.

    Safety:
        A MedicationEvent is an observation from a source, not a
        prescribing recommendation or confirmed medication truth.

    Uncertainty:
        Missing or conflicting information should remain explicit.
        Fields may be null rather than guessed.
    """

    __tablename__ = "medication_events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evidence_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("evidence.id", ondelete="SET NULL"),
        nullable=True,
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

    status: Mapped[MedicationStatus] = mapped_column(
        SqlEnum(
            MedicationStatus,
            name="medication_status",
            native_enum=False,
        ),
        default=MedicationStatus.UNKNOWN,
        nullable=False,
    )

    event_type: Mapped[MedicationEventType] = mapped_column(
        SqlEnum(
            MedicationEventType,
            name="medication_event_type",
            native_enum=False,
        ),
        nullable=False,
    )

    event_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    extraction_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )