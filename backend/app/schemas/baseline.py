"""
Structured output schemas for the MedRecon AI baseline.

Why this module exists:
    The baseline must produce machine-readable medication reconciliation
    results so its performance can be evaluated against the same ground
    truth used for the final agentic system.

Baseline philosophy:
    The baseline is intentionally simple. It does not use specialized
    agents, explicit timeline reconstruction, independent verification,
    or interaction tools.

Safety:
    Baseline outputs are evaluation artifacts generated from synthetic
    data. They must not be interpreted as clinical recommendations.
"""

from pydantic import BaseModel, Field


class BaselineMedication(BaseModel):
    """
    Represent one medication predicted by the baseline.

    Fields may be null when the baseline cannot determine them reliably.
    """

    medication_name: str = Field(
        description="Medication name extracted from the source material."
    )

    dose: str | None = Field(
        default=None,
        description="Best-supported medication dose, when available.",
    )

    frequency: str | None = Field(
        default=None,
        description="Best-supported medication frequency, when available.",
    )

    route: str | None = Field(
        default=None,
        description="Best-supported medication route, when available.",
    )

    status: str = Field(
        description=(
            "Predicted medication state such as current, discontinued, "
            "changed, conflicting, recently_added, or uncertain."
        )
    )


class BaselineDiscrepancy(BaseModel):
    """
    Represent one medication discrepancy predicted by the baseline.
    """

    medication_name: str

    type: str = Field(
        description=(
            "Discrepancy category such as dose_conflict, "
            "frequency_conflict, or status_conflict."
        )
    )

    severity: str = Field(
        default="medium",
        description="Baseline severity estimate.",
    )

    description: str | None = None


class BaselineInteraction(BaseModel):
    """
    Represent an interaction predicted by the baseline.

    The baseline does not have access to a verified drug knowledge tool.
    This field exists so we can measure whether an ungrounded baseline
    attempts to identify interaction concerns.

    Final MedRecon interaction screening will use an approved knowledge
    source rather than model memory.
    """

    medication_a: str

    medication_b: str

    severity: str

    description: str | None = None


class BaselineResult(BaseModel):
    """
    Complete structured result produced for one synthetic case.
    """

    case_id: str

    medications: list[BaselineMedication] = Field(
        default_factory=list
    )

    discrepancies: list[BaselineDiscrepancy] = Field(
        default_factory=list
    )

    interactions: list[BaselineInteraction] = Field(
        default_factory=list
    )

    notes: list[str] = Field(
        default_factory=list
    )