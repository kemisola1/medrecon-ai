"""
Intake & Extraction Agent for MedRecon AI.

Purpose:
    Convert raw medication-related source text into structured medication
    observations while preserving the original source evidence.

Why this agent exists:
    Medication reconciliation starts by extracting what each source
    actually documents.

    A single source may mention the same medication multiple times.

Example:
    "Stop oral Diclofenac. Start topical Diclofenac twice daily."

This represents two medication events:
    1. old oral Diclofenac is stopped
    2. topical Diclofenac is started

The Intake Agent must preserve both observations so later agents can
reconstruct the medication timeline correctly.

Responsibilities:
    - identify medication mentions
    - preserve multiple mentions of the same medication
    - extract dose
    - extract frequency
    - extract route
    - extract medication-status language
    - preserve source evidence
    - preserve source identifiers, types, and dates
    - flag incomplete observations

Non-responsibilities:
    - brand/generic identity resolution
    - ambiguous abbreviation expansion
    - final medication reconciliation
    - discrepancy verification
    - interaction screening
    - prescribing or treatment changes

Safety:
    The Intake Agent extracts only information supported by the source.

    Missing information remains missing.

    Consequential medication decisions remain subject to qualified human
    review.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from app.agents.base import (
    AgentStepType,
    BaseAgent,
)


# ---------------------------------------------------------------------------
# Medication vocabulary
# ---------------------------------------------------------------------------

KNOWN_MEDICATION_TERMS = {
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
    "mtx",
    "norvasc",
    "simvastatin",
    "trimethoprim-sulfamethoxazole",
    "warfarin",
}


# ---------------------------------------------------------------------------
# Frequency vocabulary
# ---------------------------------------------------------------------------

FREQUENCY_PATTERNS = (
    (
        "three times daily",
        (
            r"\bthree times daily\b",
            r"\bthree times a day\b",
            r"\btid\b",
            r"\bt\.?i\.?d\.?\b",
        ),
    ),
    (
        "twice daily",
        (
            r"\btwice daily\b",
            r"\btwice a day\b",
            r"\bbid\b",
            r"\bb\.?i\.?d\.?\b",
        ),
    ),
    (
        "once weekly",
        (
            r"\bonce weekly\b",
            r"\bonce a week\b",
            r"\bweekly\b",
        ),
    ),
    (
        "nightly",
        (
            r"\bnightly\b",
            r"\bat night\b",
        ),
    ),
    (
        "once daily",
        (
            r"\bonce daily\b",
            r"\bonce a day\b",
            r"\bdaily\b",
        ),
    ),
)


# ---------------------------------------------------------------------------
# Route vocabulary
# ---------------------------------------------------------------------------

ROUTE_PATTERNS = (
    (
        "oral",
        (
            r"\boral\b",
            r"\borally\b",
            r"\bby mouth\b",
            r"\bpo\b",
            r"\bp\.?o\.?\b",
        ),
    ),
    (
        "topical",
        (
            r"\btopical\b",
            r"\btopically\b",
        ),
    ),
)


def normalize_whitespace(
    value: str,
) -> str:
    """
    Collapse repeated whitespace.
    """
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def medication_pattern(
    medication_term: str,
) -> str:
    """
    Build a safe regex pattern for a medication name.
    """
    return (
        rf"\b{re.escape(medication_term)}\b"
    )


def find_medication_mentions(
    text: str,
) -> list[dict[str, Any]]:
    """
    Find every medication mention in the source.

    Repeated mentions of the same medication are preserved.

    Returns:
        List containing:
            medication_term
            start
            end
    """
    mentions: list[
        dict[str, Any]
    ] = []

    for medication_term in KNOWN_MEDICATION_TERMS:
        for match in re.finditer(
            medication_pattern(
                medication_term
            ),
            text,
            flags=re.IGNORECASE,
        ):
            mentions.append(
                {
                    "medication_term": medication_term,
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    mentions.sort(
        key=lambda item: item["start"]
    )

    return mentions


def find_sentence_start(
    text: str,
    position: int,
) -> int:
    """
    Find the beginning of the sentence or clause containing a position.
    """
    preceding = text[:position]

    boundary = max(
        preceding.rfind("."),
        preceding.rfind(";"),
        preceding.rfind("\n"),
    )

    return boundary + 1


def find_sentence_end(
    text: str,
    position: int,
) -> int:
    """
    Find the end of the sentence or clause containing a position.
    """
    following = text[position:]

    match = re.search(
        r"[.;\n]",
        following,
    )

    if match:
        return (
            position
            + match.start()
        )

    return len(text)


def extract_mention_context(
    text: str,
    mention_start: int,
) -> str:
    """
    Extract the complete sentence or clause containing one medication mention.
    """
    start = find_sentence_start(
        text,
        mention_start,
    )

    end = find_sentence_end(
        text,
        mention_start,
    )

    return normalize_whitespace(
        text[start:end]
    )


def extract_evidence_segment(
    text: str,
    medication_term: str,
    mention_start: int,
) -> str:
    """
    Build evidence text for a specific medication mention.
    """
    del medication_term

    return extract_mention_context(
        text,
        mention_start,
    )


def extract_dose(
    segment: str,
    medication_term: str,
) -> str | None:
    """
    Extract the best-supported medication dose.

    Explicit dose transitions use the target dose.
    """
    del medication_term

    lowered = segment.lower()

    dose_pattern = (
        r"(\d+(?:/\d+)?(?:\.\d+)?\s*"
        r"(?:mg|mcg|g|ml))"
    )

    transition_match = re.search(
        (
            rf"\bfrom\s+"
            rf"{dose_pattern}"
            rf"\s+to\s+"
            rf"{dose_pattern}"
        ),
        lowered,
        flags=re.IGNORECASE,
    )

    if transition_match:
        return normalize_whitespace(
            transition_match.group(2)
        )

    matches = re.findall(
        dose_pattern,
        segment,
        flags=re.IGNORECASE,
    )

    if not matches:
        return None

    if re.search(
        (
            r"\b("
            r"increase|increased|"
            r"decrease|decreased|"
            r"change|changed|"
            r"switch|switched"
            r")\b"
        ),
        lowered,
    ):
        return normalize_whitespace(
            matches[-1]
        )

    return normalize_whitespace(
        matches[0]
    )


def extract_frequency(
    segment: str,
) -> str | None:
    """
    Extract standardized medication frequency.

    Explicit frequency transitions use the target frequency.
    """
    lowered = segment.lower()

    detected: list[
        tuple[int, str]
    ] = []

    for (
        frequency,
        patterns,
    ) in FREQUENCY_PATTERNS:

        for pattern in patterns:
            match = re.search(
                pattern,
                lowered,
                flags=re.IGNORECASE,
            )

            if match:
                detected.append(
                    (
                        match.start(),
                        frequency,
                    )
                )

    if not detected:
        return None

    detected.sort(
        key=lambda item: item[0]
    )

    transition_language = re.search(
        (
            r"\b("
            r"from|"
            r"change|changed|"
            r"increase|increased|"
            r"decrease|decreased|"
            r"switch|switched"
            r")\b"
        ),
        lowered,
    )

    if transition_language:
        return detected[-1][1]

    return detected[0][1]


def extract_route(
    segment: str,
) -> str | None:
    """
    Extract standardized medication route.
    """
    lowered = segment.lower()

    detected: list[
        tuple[int, str]
    ] = []

    for (
        route,
        patterns,
    ) in ROUTE_PATTERNS:

        for pattern in patterns:
            match = re.search(
                pattern,
                lowered,
                flags=re.IGNORECASE,
            )

            if match:
                detected.append(
                    (
                        match.start(),
                        route,
                    )
                )

    if not detected:
        return None

    detected.sort(
        key=lambda item: item[0]
    )

    if (
        len(detected) > 1
        and re.search(
            (
                r"\b("
                r"stop|stopped|"
                r"start|started|"
                r"change|changed|"
                r"switch|switched"
                r")\b"
            ),
            lowered,
        )
    ):
        return detected[-1][1]

    return detected[0][1]


def extract_status_text(
    context: str,
) -> str | None:
    """
    Extract medication status from the specific mention context.
    """
    lowered = context.lower()

    status_patterns = (
        (
            "discontinued",
            (
                r"\bdiscontinued\b",
                r"\bstopped\b",
                r"\bstop\b",
                r"\bno longer taking\b",
                r"\bno longer uses\b",
            ),
        ),
        (
            "restarted",
            (
                r"\brestarted\b",
                r"\brestart\b",
            ),
        ),
        (
            "increased",
            (
                r"\bincreased\b",
                r"\bincrease\b",
            ),
        ),
        (
            "decreased",
            (
                r"\bdecreased\b",
                r"\bdecrease\b",
            ),
        ),
        (
            "changed",
            (
                r"\bchanged\b",
                r"\bchange\b",
                r"\bswitched\b",
                r"\bswitch\b",
            ),
        ),
        (
            "started",
            (
                r"\bnewly started\b",
                r"\bstarted\b",
                r"\bstart\b",
            ),
        ),
        (
            "continued",
            (
                r"\bcontinued\b",
                r"\bcontinues\b",
                r"\bcontinue\b",
            ),
        ),
    )

    for (
        status,
        patterns,
    ) in status_patterns:

        for pattern in patterns:
            if re.search(
                pattern,
                lowered,
                flags=re.IGNORECASE,
            ):
                return status

    return None


def calculate_extraction_confidence(
    medication_name_raw: str | None,
    dose: str | None,
    frequency: str | None,
    route: str | None,
) -> float:
    """
    Calculate extraction completeness.

    This score is NOT clinical confidence.

    Weighting:
        medication = 0.40
        dose = 0.20
        frequency = 0.20
        route = 0.20
    """
    confidence = 0.0

    if medication_name_raw:
        confidence += 0.4

    if dose:
        confidence += 0.2

    if frequency:
        confidence += 0.2

    if route:
        confidence += 0.2

    return round(
        confidence,
        2,
    )


def observation_needs_verification(
    medication_name_raw: str | None,
    dose: str | None,
    frequency: str | None,
    route: str | None,
) -> bool:
    """
    Flag incomplete extraction for downstream verification.

    Route absence alone does not automatically create a review requirement.
    """
    del route

    if medication_name_raw is None:
        return True

    if dose is None:
        return True

    if frequency is None:
        return True

    return False


class IntakeExtractionAgent(
    BaseAgent
):
    """
    Convert raw case sources into structured medication observations.
    """

    agent_name = (
        "Intake & Extraction Agent"
    )

    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extract medication observations from every source.
        """
        case_id = payload.get(
            "case_id"
        )

        sources = payload.get(
            "sources"
        )

        if not case_id:
            raise ValueError(
                "Intake Agent requires case_id."
            )

        if sources is None:
            raise ValueError(
                "Intake Agent requires sources."
            )

        if not isinstance(
            sources,
            list,
        ):
            raise ValueError(
                "Intake Agent sources must be a list."
            )

        self.record_step(
            AgentStepType.VALIDATION,
            "Validated case input for medication extraction.",
            {
                "case_id": case_id,
                "source_count": len(
                    sources
                ),
            },
        )

        observations: list[
            dict[str, Any]
        ] = []

        for source in sources:
            source_observations = (
                self._process_source(
                    case_id=case_id,
                    source=source,
                )
            )

            observations.extend(
                source_observations
            )

        self.record_step(
            AgentStepType.DECISION,
            "Completed medication extraction across all sources.",
            {
                "case_id": case_id,
                "observation_count": len(
                    observations
                ),
            },
        )

        return {
            "case_id": case_id,
            "observations": observations,
            "observation_count": len(
                observations
            ),
        }

    def _process_source(
        self,
        case_id: str,
        source: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Extract every medication mention from one source.

        Source provenance is preserved for downstream reconciliation.

        Synthetic and API inputs may use either:
            "type"
        or:
            "source_type"

        Both are accepted to prevent provenance loss.
        """
        source_id = source.get(
            "source_id"
        )

        #
        # Preserve source provenance.
        #
        # Synthetic cases use "type", while some structured/API inputs may
        # use "source_type". Prefer source_type when explicitly supplied,
        # otherwise fall back to type.
        #
        source_type = (
            source.get("source_type")
            or source.get("type")
        )

        source_date = (
            source.get("date")
            or source.get("source_date")
        )

        text = (
            source.get("text")
            or source.get("content")
            or ""
        )

        if not isinstance(
            text,
            str,
        ):
            text = str(text)

        text = text.strip()

        if not text:
            self.record_step(
                AgentStepType.VALIDATION,
                "Source contained no extractable text.",
                {
                    "source_id": source_id,
                    "source_type": source_type,
                },
            )

            return []

        mentions = (
            find_medication_mentions(
                text
            )
        )

        self.record_step(
            AgentStepType.DECISION,
            "Identified medication mentions in source.",
            {
                "source_id": source_id,
                "source_type": source_type,
                "mention_count": len(
                    mentions
                ),
                "medication_terms": [
                    mention[
                        "medication_term"
                    ]
                    for mention in mentions
                ],
            },
        )

        observations: list[
            dict[str, Any]
        ] = []

        for mention in mentions:
            medication_term = (
                mention[
                    "medication_term"
                ]
            )

            mention_start = (
                mention[
                    "start"
                ]
            )

            context = (
                extract_mention_context(
                    text,
                    mention_start,
                )
            )

            evidence_segment = (
                extract_evidence_segment(
                    text=text,
                    medication_term=(
                        medication_term
                    ),
                    mention_start=(
                        mention_start
                    ),
                )
            )

            dose = extract_dose(
                evidence_segment,
                medication_term,
            )

            frequency = (
                extract_frequency(
                    evidence_segment
                )
            )

            route = (
                extract_route(
                    evidence_segment
                )
            )

            status_text = (
                extract_status_text(
                    context
                )
            )

            confidence = (
                calculate_extraction_confidence(
                    medication_name_raw=(
                        medication_term
                    ),
                    dose=dose,
                    frequency=frequency,
                    route=route,
                )
            )

            needs_verification = (
                observation_needs_verification(
                    medication_name_raw=(
                        medication_term
                    ),
                    dose=dose,
                    frequency=frequency,
                    route=route,
                )
            )

            observation = {
                "observation_id": str(
                    uuid4()
                ),
                "case_id": case_id,
                "medication_name_raw": (
                    medication_term
                ),
                "dose": dose,
                "frequency": frequency,
                "route": route,
                "status_text": status_text,
                "source_id": source_id,
                "source_type": source_type,
                "source_date": source_date,
                "evidence_text": (
                    evidence_segment
                ),
                "extraction_confidence": (
                    confidence
                ),
                "needs_verification": (
                    needs_verification
                ),
            }

            observations.append(
                observation
            )

            self.record_step(
                AgentStepType.OUTPUT_CREATED,
                "Created medication observation.",
                {
                    "medication_name_raw": (
                        medication_term
                    ),
                    "dose": dose,
                    "frequency": frequency,
                    "route": route,
                    "status_text": (
                        status_text
                    ),
                    "source_id": source_id,
                    "source_type": (
                        source_type
                    ),
                    "needs_verification": (
                        needs_verification
                    ),
                },
            )

        return observations