"""
Database model for potential medication interaction findings.

Interaction findings are created only after the medication set has
been reconciled so that safety screening is based on the best-supported
current medication picture rather than every historical mention.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.discrepancy import VerificationStatus


class InteractionSeverity(str, Enum):
    """
    Priority level associated with a potential interaction finding.

    HIGH:
        Potentially important safety concern requiring prompt review.

    MEDIUM:
        Clinically relevant interaction signal that should be reviewed.

    LOW:
        Lower-priority interaction signal.

    UNKNOWN:
        Severity was not supplied by the designated knowledge source.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class InteractionFinding(TimestampMixin, Base):
    """
    Store one potential medication interaction finding.

    Why this exists:
        MedRecon AI screens the reconciled medication set for possible
        medication interactions and preserves those findings for
        verification and qualified human review.

    Fields:
        id:
            Internal unique identifier.

        case_id:
            Reconciliation case where the interaction was identified.

        medication_a_id:
            First reconciled medication involved.

        medication_b_id:
            Second reconciled medication involved.

        description:
            Human-readable description of the potential interaction.

        severity:
            Priority supplied or derived from the designated knowledge
            source.

        evidence_source:
            Name or identifier of the medication knowledge source used.

        verification_status:
            Whether the interaction finding has been verified.

        requires_human_review:
            Indicates whether qualified review is required.

    Safety:
        This record represents a potential interaction signal only.

        MedRecon AI must not recommend starting, stopping, or changing
        medication therapy based solely on this finding.

        Interaction facts should come from a designated medication
        knowledge source rather than unsupported model memory.

    Uncertainty:
        If interaction evidence is unavailable, ambiguous, or cannot be
        verified, the finding should remain UNVERIFIED.
    """

    __tablename__ = "interaction_findings"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    medication_a_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "reconciled_medications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    medication_b_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "reconciled_medications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[InteractionSeverity] = mapped_column(
        SqlEnum(
            InteractionSeverity,
            name="interaction_severity",
            native_enum=False,
        ),
        default=InteractionSeverity.UNKNOWN,
        nullable=False,
    )

    evidence_source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        SqlEnum(
            VerificationStatus,
            name="interaction_verification_status",
            native_enum=False,
        ),
        default=VerificationStatus.UNVERIFIED,
        nullable=False,
    )

    requires_human_review: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )