"""
Database model for evidence captured from MedRecon source material.

Evidence records preserve the exact supporting excerpt and location
used by agents and reviewers when evaluating medication information.
"""

from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Evidence(TimestampMixin, Base):
    """
    Store a traceable piece of evidence from a MedRecon source.

    Why this exists:
        MedRecon AI should not produce medication findings that cannot
        be traced back to supporting source material.

    Fields:
        id:
            Internal unique identifier.

        source_id:
            Source document or input that contains this evidence.

        text:
            Exact supporting excerpt or extracted text.

        page_number:
            Optional page number for PDFs or scanned documents.

        start_offset:
            Optional character offset where the evidence begins.

        end_offset:
            Optional character offset where the evidence ends.

        confidence:
            Extraction confidence from 0.0 to 1.0 when available.

    Safety:
        Evidence supports a finding but does not by itself establish
        that the medication information is clinically correct or current.

    Uncertainty:
        Low-confidence or incomplete evidence should remain traceable
        and can later trigger verification or human review.
    """

    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    start_offset: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    end_offset: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )



''' 
The key idea here is that MedRecon will be able to answer:
Why did you flag this medication?
Which source said it?
What exact text supported it?
Where in the document was it?
How confident was the extraction? 

'''