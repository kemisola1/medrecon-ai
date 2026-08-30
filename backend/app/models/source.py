"""
Database model for information sources used in MedRecon AI.

A Source represents where medication-related information came from,
such as a prescription, discharge summary, clinical note, pharmacy
record, patient-reported list, image, manual entry, or API feed.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SourceType(str, Enum):
    """
    Allowed source categories for MedRecon AI.

    These values describe the origin of medication information and
    support traceability throughout the reconciliation workflow.
    """

    EMR = "emr"
    PRESCRIPTION = "prescription"
    DISCHARGE_SUMMARY = "discharge_summary"
    CLINICAL_NOTE = "clinical_note"
    PHARMACY = "pharmacy"
    PATIENT_REPORT = "patient_report"
    IMAGE = "image"
    MANUAL = "manual"
    API = "api"


class Source(TimestampMixin, Base):
    """
    Store one source of medication-related information.

    Why this exists:
        MedRecon AI must preserve where every medication observation
        originated. This supports evidence-backed reconciliation,
        verification, and human review.

    Fields:
        id:
            Internal unique identifier for the source.

        case_id:
            The reconciliation case this source belongs to.

        source_type:
            Category describing where the information came from.

        name:
            Human-readable source name, such as
            "Discharge Summary - August 2026".

    Safety:
        A source is evidence input only. Its presence does not mean
        its contents are correct or clinically current.

    Uncertainty:
        Conflicting sources are preserved rather than overwritten.
        Later agents will evaluate chronology, consistency, and
        supporting evidence.
    """

    __tablename__ = "sources"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_type: Mapped[SourceType] = mapped_column(
        SqlEnum(
            SourceType,
            name="source_type",
            native_enum=False,
        ),
        nullable=False,
    )


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )