"""
Database model for medication discrepancies detected by MedRecon AI.

A Discrepancy represents a conflict, inconsistency, duplication, or
missing medication detail identified during reconciliation.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DiscrepancyType(str, Enum):
    """
    Types of medication discrepancies MedRecon can detect.
    """

    DOSE_CONFLICT = "dose_conflict"
    FREQUENCY_CONFLICT = "frequency_conflict"
    ROUTE_CONFLICT = "route_conflict"
    STATUS_CONFLICT = "status_conflict"
    DUPLICATE = "duplicate"
    TEMPORAL_CONFLICT = "temporal_conflict"
    MISSING_INFORMATION = "missing_information"


class DiscrepancySeverity(str, Enum):
    """
    Priority level assigned to a discrepancy.

    HIGH:
        Potentially important medication-safety concern requiring
        prompt human review.

    MEDIUM:
        Meaningful inconsistency that should be reviewed.

    LOW:
        Lower-priority issue that may still affect reconciliation.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationStatus(str, Enum):
    """
    Verification outcome assigned after evidence review.

    VERIFIED:
        Available evidence sufficiently supports the finding.

    UNVERIFIED:
        Evidence is incomplete or insufficient.

    REJECTED:
        Verification determined that the finding is not adequately
        supported by the available evidence.
    """

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    REJECTED = "rejected"


class Discrepancy(TimestampMixin, Base):
    """
    Store one medication discrepancy detected during reconciliation.

    Why this exists:
        Medication reconciliation is valuable because multiple sources
        may disagree. These disagreements must be preserved explicitly
        rather than silently resolved or overwritten.

    Fields:
        id:
            Internal unique discrepancy identifier.

        case_id:
            Reconciliation case containing the discrepancy.

        reconciled_medication_id:
            Optional reconciled medication related to this discrepancy.

        discrepancy_type:
            Category of inconsistency detected.

        description:
            Human-readable explanation of the discrepancy.

        severity:
            Priority assigned to the finding.

        verification_status:
            Outcome of the Verification Agent.

        requires_human_review:
            Whether a qualified reviewer should examine the finding.

    Safety:
        A discrepancy is a review finding, not a prescribing instruction.

        MedRecon does not automatically modify, stop, or start medications
        based on a discrepancy.

    Uncertainty:
        Findings without sufficient supporting evidence should remain
        UNVERIFIED rather than being presented as confirmed facts.
    """

    __tablename__ = "discrepancies"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reconciled_medication_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "reconciled_medications.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    discrepancy_type: Mapped[DiscrepancyType] = mapped_column(
        SqlEnum(
            DiscrepancyType,
            name="discrepancy_type",
            native_enum=False,
        ),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[DiscrepancySeverity] = mapped_column(
        SqlEnum(
            DiscrepancySeverity,
            name="discrepancy_severity",
            native_enum=False,
        ),
        default=DiscrepancySeverity.MEDIUM,
        nullable=False,
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        SqlEnum(
            VerificationStatus,
            name="verification_status",
            native_enum=False,
        ),
        default=VerificationStatus.UNVERIFIED,
        nullable=False,
    )

    requires_human_review: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )


    '''
    Important design:
    Reconciled_medication_id is optional because, 
    some discrepancies may concern the overall case or 
    an unresolved identity conflict rather than a medication that has already been fully reconciled. 
    Also, verification_status defaults to UNVERIFIED, 
    which supports our “prove it” Verification Agent instead of letting raw detections masquerade as confirmed facts.
    '''