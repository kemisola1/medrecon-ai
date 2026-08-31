"""
Simple baseline medication reconciliation service for MedRecon AI.

Why this module exists:
    The hackathon requires a meaningful baseline that can be evaluated
    against the same synthetic cases as the final agentic workflow.

    This baseline intentionally uses lightweight deterministic rules and
    one-pass reconciliation. It does not use specialized agents, explicit
    verification, or a medication knowledge tool.

Purpose:
    Provide a reproducible V0 benchmark that is simple enough to improve
    upon while still producing useful structured output.

Safety:
    This service is for synthetic hackathon evaluation only.
    It does not provide clinical recommendations and must not be used
    to make medication decisions for real patients.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.schemas.baseline import (
    BaselineDiscrepancy,
    BaselineMedication,
    BaselineResult,
)


KNOWN_MEDICATIONS = {
    "amlodipine",
    "atenolol",
    "atorvastatin",
    "bisoprolol",
    "diclofenac",
    "furosemide",
    "gabapentin",
    "lisinopril",
    "losartan",
    "metformin",
    "norvasc",
    "simvastatin",
    "trimethoprim-sulfamethoxazole",
    "warfarin",
}


BRAND_TO_GENERIC = {
    "norvasc": "amlodipine",
}


FREQUENCY_PATTERNS = {
    "once daily": [
        r"\bonce daily\b",
        r"\bdaily\b",
    ],
    "twice daily": [
        r"\btwice daily\b",
        r"\btwo times daily\b",
    ],
    "three times daily": [
        r"\bthree times daily\b",
    ],
    "once weekly": [
        r"\bonce weekly\b",
        r"\bweekly\b",
    ],
    "nightly": [
        r"\bnightly\b",
    ],
}


@dataclass
class MedicationMention:
    """
    Internal representation of one medication mention found in source text.

    This is deliberately much simpler than the final MedicationEvent model.

    Attributes:
        medication_name:
            Normalized medication name.

        dose:
            Extracted dose when present.

        frequency:
            Extracted frequency when present.

        route:
            Extracted route when present.

        status_hint:
            Simple text-derived state such as current or discontinued.

        source_date:
            Source document date, used only for basic ordering.
    """

    medication_name: str
    dose: str | None
    frequency: str | None
    route: str | None
    status_hint: str
    source_date: str


def normalize_medication_name(name: str) -> str:
    """
    Normalize a medication name using the baseline's small lookup table.

    Args:
        name:
            Medication name found in source text.

    Returns:
        Canonical display form.

    Limitation:
        The baseline recognizes only a small hard-coded vocabulary.
        The final Medication Identity Agent will use a stronger controlled
        normalization process and preserve ambiguity rather than guessing.
    """
    normalized = name.strip().lower()

    normalized = BRAND_TO_GENERIC.get(
        normalized,
        normalized,
    )

    return normalized.title()


def extract_dose(
    text: str,
    medication_name: str,
) -> str | None:
    """
    Extract a nearby numeric medication dose.

    Args:
        text:
            Source text.

        medication_name:
            Medication name used to locate the relevant text region.

    Returns:
        Dose such as "500 mg" or "160/800 mg", otherwise None.

    Failure modes:
        This lightweight rule may miss unusual dose formats or associate
        a nearby dose incorrectly in complex text.

        Those weaknesses are intentional baseline limitations.
    """
    escaped_name = re.escape(
        medication_name
    )

    pattern = (
        rf"{escaped_name}"
        rf".{{0,45}}?"
        rf"(\d+(?:/\d+)?(?:\.\d+)?\s*(?:mg|mcg|g|ml))"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return re.sub(
        r"\s+",
        " ",
        match.group(1).strip(),
    )


def extract_frequency(
    text: str,
    medication_name: str,
) -> str | None:
    """
    Extract the frequency associated with one medication mention.

    Why:
        A source can contain multiple medications. Searching too large a
        text window can cause one medication to incorrectly inherit
        another medication's frequency.

    Strategy:
        Inspect only the local sentence beginning at the medication name.

        More specific frequency expressions are checked before generic
        expressions such as "daily".

    Args:
        text:
            Full source text.

        medication_name:
            Medication whose local sentence should be inspected.

    Returns:
        Normalized frequency when found, otherwise None.

    Limitation:
        This remains a lightweight baseline rule and may fail on complex
        narrative documentation.
    """
    medication_match = re.search(
        re.escape(medication_name),
        text,
        flags=re.IGNORECASE,
    )

    if not medication_match:
        return None

    start = medication_match.start()

    remaining_text = text[start:]

    # Restrict extraction to the current sentence so a later medication
    # cannot donate its frequency to the current medication.
    sentence = remaining_text.split(
        ".",
        1,
    )[0].lower()

    # Specific patterns are checked before "once daily" because the
    # generic "daily" expression could otherwise match "twice daily".
    ordered_frequencies = (
        "three times daily",
        "twice daily",
        "once weekly",
        "nightly",
        "once daily",
    )

    for frequency in ordered_frequencies:
        patterns = FREQUENCY_PATTERNS[
            frequency
        ]

        for pattern in patterns:
            if re.search(
                pattern,
                sentence,
            ):
                return frequency

    return None


def extract_route(
    text: str,
    medication_name: str,
) -> str | None:
    """
    Extract the administration route associated with a medication.

    Why:
        Route extraction should remain local to the medication being
        processed rather than borrowing information from another
        medication later in the document.

    Args:
        text:
            Full synthetic source text.

        medication_name:
            Medication whose local sentence should be inspected.

    Returns:
        "oral", "topical", or None when no supported route is found.

    Limitation:
        This intentionally supports only the small route vocabulary
        required by the synthetic baseline dataset.
    """
    medication_match = re.search(
        re.escape(medication_name),
        text,
        flags=re.IGNORECASE,
    )

    if not medication_match:
        return None

    start = medication_match.start()

    # Restrict route extraction to the medication's local sentence.
    sentence = text[start:].split(
        ".",
        1,
    )[0].lower()

    if "orally" in sentence:
        return "oral"

    if re.search(
        r"\boral\b",
        sentence,
    ):
        return "oral"

    if "topically" in sentence:
        return "topical"

    if re.search(
        r"\btopical\b",
        sentence,
    ):
        return "topical"

    return None


def infer_status_hint(
    text: str,
    medication_name: str,
) -> str:
    """
    Infer a crude medication status from nearby wording.

    Args:
        text:
            Complete source text.

        medication_name:
            Medication being evaluated.

    Returns:
        One of:
            current
            discontinued
            recently_added
            changed

    Limitation:
        This is simple pattern matching rather than full temporal
        medication-state reasoning.
    """
    medication_match = re.search(
        re.escape(medication_name),
        text,
        flags=re.IGNORECASE,
    )

    if not medication_match:
        return "current"

    start = max(
        0,
        medication_match.start() - 45,
    )

    end = medication_match.end() + 100

    nearby = text[start:end].lower()

    if any(
        phrase in nearby
        for phrase in (
            "discontinued",
            "stop ",
            "stopped",
            "no longer",
        )
    ):
        return "discontinued"

    if any(
        phrase in nearby
        for phrase in (
            "restart ",
            "restarted",
            "start ",
            "started",
        )
    ):
        return "recently_added"

    if any(
        phrase in nearby
        for phrase in (
            "increase ",
            "decrease ",
            "change ",
            "changed",
        )
    ):
        return "changed"

    return "current"


def extract_mentions(
    source: dict[str, Any],
) -> list[MedicationMention]:
    """
    Extract medication mentions from one synthetic source document.

    Args:
        source:
            Synthetic source object containing text and date.

    Returns:
        Medication mentions found by the baseline.

    Uncertainty:
        Only medications from the baseline vocabulary are recognized.

        Irrelevant medication mentions may also be incorrectly treated
        as patient medications. This is an intentional weakness that
        adversarial evaluation cases can expose.
    """
    text = source.get(
        "text",
        "",
    )

    source_date = source.get(
        "date",
        "",
    )

    mentions: list[
        MedicationMention
    ] = []

    for medication in sorted(
        KNOWN_MEDICATIONS
    ):
        if not re.search(
            rf"\b{re.escape(medication)}\b",
            text,
            flags=re.IGNORECASE,
        ):
            continue

        mention = MedicationMention(
            medication_name=(
                normalize_medication_name(
                    medication
                )
            ),
            dose=extract_dose(
                text,
                medication,
            ),
            frequency=extract_frequency(
                text,
                medication,
            ),
            route=extract_route(
                text,
                medication,
            ),
            status_hint=infer_status_hint(
                text,
                medication,
            ),
            source_date=source_date,
        )

        mentions.append(
            mention
        )

    return mentions


def reconcile_mentions(
    mentions: list[MedicationMention],
) -> tuple[
    list[BaselineMedication],
    list[BaselineDiscrepancy],
]:
    """
    Perform simple one-pass medication reconciliation.

    Strategy:
        Group mentions by normalized medication name.

        Prefer the newest mention for medication state.

        When the newest source omits a dose, frequency, or route, preserve
        the most recent previously documented non-null value rather than
        treating the omission as evidence that the attribute disappeared.

        If sources contain conflicting non-null values and there is no
        explicit change signal, classify the medication as conflicting.

    Args:
        mentions:
            Medication mentions extracted from all case sources.

    Returns:
        Tuple containing:
            reconciled baseline medications
            detected baseline discrepancies

    Limitation:
        This is still a lightweight baseline. It does not construct a full
        medication-event timeline, rank source reliability, or independently
        verify evidence.
    """
    grouped: dict[
        str,
        list[MedicationMention],
    ] = {}

    for mention in mentions:
        grouped.setdefault(
            mention.medication_name,
            [],
        ).append(
            mention
        )

    medications: list[
        BaselineMedication
    ] = []

    discrepancies: list[
        BaselineDiscrepancy
    ] = []

    for medication_name, group in sorted(
        grouped.items()
    ):
        ordered = sorted(
            group,
            key=lambda item: item.source_date,
        )

        newest = ordered[-1]

        doses = {
            item.dose
            for item in ordered
            if item.dose is not None
        }

        frequencies = {
            item.frequency
            for item in ordered
            if item.frequency is not None
        }

        routes = {
            item.route
            for item in ordered
            if item.route is not None
        }

        explicit_change = (
            newest.status_hint
            in {
                "changed",
                "recently_added",
                "discontinued",
            }
        )

        status = newest.status_hint

        # Begin with the newest explicitly documented values.
        dose = newest.dose
        frequency = newest.frequency
        route = newest.route

        # A newer source may mention that a medication is continued while
        # omitting an attribute such as route. Omission alone should not
        # erase a previously supported value.
        if dose is None:
            for item in reversed(
                ordered[:-1]
            ):
                if item.dose is not None:
                    dose = item.dose
                    break

        if frequency is None:
            for item in reversed(
                ordered[:-1]
            ):
                if item.frequency is not None:
                    frequency = item.frequency
                    break

        if route is None:
            for item in reversed(
                ordered[:-1]
            ):
                if item.route is not None:
                    route = item.route
                    break

        if (
            len(doses) > 1
            and not explicit_change
        ):
            status = "conflicting"
            dose = None

            discrepancies.append(
                BaselineDiscrepancy(
                    medication_name=(
                        medication_name
                    ),
                    type="dose_conflict",
                    severity="medium",
                    description=(
                        "Multiple sources contain "
                        "different medication doses."
                    ),
                )
            )

        if (
            len(frequencies) > 1
            and not explicit_change
        ):
            status = "conflicting"
            frequency = None

            discrepancies.append(
                BaselineDiscrepancy(
                    medication_name=(
                        medication_name
                    ),
                    type="frequency_conflict",
                    severity="medium",
                    description=(
                        "Multiple sources contain "
                        "different medication frequencies."
                    ),
                )
            )

        if (
            len(routes) > 1
            and not explicit_change
        ):
            status = "conflicting"
            route = None

            discrepancies.append(
                BaselineDiscrepancy(
                    medication_name=(
                        medication_name
                    ),
                    type="route_conflict",
                    severity="medium",
                    description=(
                        "Multiple sources contain "
                        "different medication routes."
                    ),
                )
            )

        if (
            (
                dose is None
                or frequency is None
            )
            and status == "current"
        ):
            status = "uncertain"

            discrepancies.append(
                BaselineDiscrepancy(
                    medication_name=(
                        medication_name
                    ),
                    type="missing_information",
                    severity="low",
                    description=(
                        "Medication documentation "
                        "is incomplete."
                    ),
                )
            )

        medications.append(
            BaselineMedication(
                medication_name=(
                    medication_name
                ),
                dose=dose,
                frequency=frequency,
                route=route,
                status=status,
            )
        )

    return medications, discrepancies


def run_baseline(
    case: dict[str, Any],
) -> BaselineResult:
    """
    Run the V0 baseline on one synthetic reconciliation case.

    Args:
        case:
            Synthetic case dictionary.

    Returns:
        Structured BaselineResult.

    Important:
        Ground-truth data is never passed into this function.

    Safety:
        This performs hackathon evaluation on synthetic text only.
    """
    mentions: list[
        MedicationMention
    ] = []

    for source in case.get(
        "sources",
        [],
    ):
        mentions.extend(
            extract_mentions(
                source
            )
        )

    medications, discrepancies = (
        reconcile_mentions(
            mentions
        )
    )

    return BaselineResult(
        case_id=case[
            "case_id"
        ],
        medications=medications,
        discrepancies=discrepancies,
        interactions=[],
        notes=[
            (
                "V0 baseline uses lightweight "
                "deterministic extraction and "
                "one-pass reconciliation."
            )
        ],
    )

