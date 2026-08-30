"""
Database model for qualified human review in MedRecon AI.

HumanReview stores reviewer decisions on discrepancies, interaction
findings, or other reconciliation outputs that require human oversight.
"""

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ReviewDecision(str, Enum):
    """
    Allowed reviewer decisions.

    ACCEPTED:
        The reviewer accepts the finding as sufficiently supported.

    REJECTED:
        The reviewer determines that the finding should not be accepted.

    NEEDS_CLARIFICATION:
        Available evidence is insufficient and additional information
        or clarification is required.
    """

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_CLARIFICATION = "needs_clarification"


class HumanReview(TimestampMixin, Base):
    """
    Store one qualified human-review decision.

    Why this exists:
        MedRecon AI may identify medication discrepancies or potential
        interaction signals, but those findings should not automatically
        trigger clinical actions.

        HumanReview creates an explicit checkpoint where a qualified
        reviewer can accept, reject, or request clarification.

    Fields:
        id:
            Unique review identifier.

        case_id:
            Reconciliation case being reviewed.

        discrepancy_id:
            Optional discrepancy associated with this review.

        interaction_finding_id:
            Optional interaction finding associated with this review.

        decision:
            Reviewer's final decision.

        reviewer_name:
            Optional reviewer display name for demo and audit purposes.

        reviewer_role:
            Optional professional role, such as pharmacist or clinician.

        note:
            Optional explanation or clarification entered by the reviewer.

    Safety:
        This model records human decisions only.

        It does not itself prescribe, discontinue, modify, or administer
        medication.

    Privacy:
        Hackathon demonstrations should use synthetic reviewer identities
        rather than unnecessary real personal data.
    """

    __tablename__ = "human_reviews"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    discrepancy_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("discrepancies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    interaction_finding_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "interaction_findings.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    decision: Mapped[ReviewDecision] = mapped_column(
        SqlEnum(
            ReviewDecision,
            name="review_decision",
            native_enum=False,
        ),
        nullable=False,
    )

    reviewer_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    reviewer_role: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )