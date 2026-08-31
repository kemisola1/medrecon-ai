"""
Medication Identity Agent for MedRecon AI.

Purpose:
    Normalize medication observations into canonical medication identities
    while preserving ambiguity when identity cannot be safely resolved.

Why this agent exists:
    Medication reconciliation depends on knowing whether different names
    refer to the same medication.

    For example:
        Norvasc -> Amlodipine

    Without identity normalization, the system could incorrectly treat
    brand and generic names as separate medications.

Responsibilities:
    - normalize known generic medication names
    - map supported brand names to generic names
    - preserve raw medication terms
    - flag ambiguous abbreviations
    - attach identity confidence
    - preserve source provenance
    - identify observations requiring verification

Non-responsibilities:
    - deciding whether a medication is current
    - deciding whether one source is more reliable
    - resolving dose or frequency conflicts
    - screening interactions
    - prescribing, discontinuing, or changing therapy

Safety:
    Medication identity must not be guessed when ambiguous.

    Uncertain identity is explicitly preserved for downstream verification
    and human review.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import (
    AgentStepType,
    BaseAgent,
)


BRAND_TO_GENERIC = {
    "norvasc": "amlodipine",
}


CANONICAL_MEDICATIONS = {
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
    "simvastatin",
    "trimethoprim-sulfamethoxazole",
    "warfarin",
}


AMBIGUOUS_TERMS = {
    "mtx",
}


def normalize_text(
    value: str,
) -> str:
    """
    Normalize medication text for matching.

    Args:
        value:
            Raw medication term.

    Returns:
        Lowercase whitespace-normalized text.
    """
    return " ".join(
        value.strip().lower().split()
    )


def title_medication(
    medication_name: str,
) -> str:
    """
    Convert a normalized medication name into display form.

    Args:
        medication_name:
            Canonical lowercase medication name.

    Returns:
        Human-readable medication name.
    """
    return medication_name.title()


def resolve_identity(
    medication_name_raw: str,
) -> dict[str, Any]:
    """
    Resolve one raw medication name into an identity result.

    Args:
        medication_name_raw:
            Medication term extracted by the Intake Agent.

    Returns:
        Dictionary containing:
            canonical_name
            identity_status
            identity_confidence
            identity_reason
            needs_verification

    Decision rules:
        1. Known brand names map to canonical generics.
        2. Known generic names are preserved.
        3. Known ambiguous abbreviations remain unresolved.
        4. Unknown terms remain unresolved rather than guessed.

    Safety:
        Ambiguous medication identity is never silently resolved.
    """
    normalized = normalize_text(
        medication_name_raw
    )

    if normalized in BRAND_TO_GENERIC:
        canonical = BRAND_TO_GENERIC[
            normalized
        ]

        return {
            "canonical_name": (
                title_medication(
                    canonical
                )
            ),
            "identity_status": (
                "resolved_brand_to_generic"
            ),
            "identity_confidence": 1.0,
            "identity_reason": (
                "Known brand-to-generic mapping."
            ),
            "needs_verification": False,
        }

    if normalized in CANONICAL_MEDICATIONS:
        return {
            "canonical_name": (
                title_medication(
                    normalized
                )
            ),
            "identity_status": (
                "resolved_generic"
            ),
            "identity_confidence": 1.0,
            "identity_reason": (
                "Medication matches controlled "
                "canonical vocabulary."
            ),
            "needs_verification": False,
        }

    if normalized in AMBIGUOUS_TERMS:
        return {
            "canonical_name": None,
            "identity_status": "ambiguous",
            "identity_confidence": 0.0,
            "identity_reason": (
                "Medication term is an ambiguous "
                "abbreviation and was not expanded."
            ),
            "needs_verification": True,
        }

    return {
        "canonical_name": None,
        "identity_status": "unresolved",
        "identity_confidence": 0.0,
        "identity_reason": (
            "Medication term is not present in the "
            "controlled identity vocabulary."
        ),
        "needs_verification": True,
    }


class MedicationIdentityAgent(BaseAgent):
    """
    Normalize medication observations into canonical identities.

    Input:
        {
            "case_id": "...",
            "observations": [...]
        }

    Output:
        {
            "case_id": "...",
            "identified_observations": [...],
            "resolved_count": ...,
            "unresolved_count": ...
        }

    Failure modes:
        - medication not present in controlled vocabulary
        - ambiguous abbreviation
        - missing medication_name_raw

    Retry policy:
        This deterministic identity layer does not automatically retry.

        Unresolved medication identities are preserved and routed to
        verification instead of being guessed.
    """

    agent_name = "medication_identity_agent"

    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve medication identity for all extracted observations.

        Args:
            payload:
                Output from the Intake & Extraction Agent.

        Returns:
            Structured identified observations.

        Raises:
            ValueError:
                If required payload fields are absent.
        """
        case_id = payload.get(
            "case_id"
        )

        if not case_id:
            raise ValueError(
                "Medication Identity Agent "
                "requires case_id."
            )

        observations = payload.get(
            "observations"
        )

        if not isinstance(
            observations,
            list,
        ):
            raise ValueError(
                "Medication Identity Agent requires "
                "an observations list."
            )

        self.record_step(
            AgentStepType.VALIDATION,
            "Validated medication observation input.",
            {
                "case_id": case_id,
                "observation_count": len(
                    observations
                ),
            },
        )

        identified_observations: list[
            dict[str, Any]
        ] = []

        resolved_count = 0
        unresolved_count = 0

        for observation in observations:
            identified = (
                self._identify_observation(
                    observation
                )
            )

            identified_observations.append(
                identified
            )

            if identified[
                "canonical_name"
            ] is None:
                unresolved_count += 1

            else:
                resolved_count += 1

        self.record_step(
            AgentStepType.DECISION,
            "Medication identity resolution completed.",
            {
                "resolved_count": resolved_count,
                "unresolved_count": (
                    unresolved_count
                ),
            },
        )

        return {
            "case_id": case_id,
            "identified_observations": (
                identified_observations
            ),
            "observation_count": len(
                identified_observations
            ),
            "resolved_count": resolved_count,
            "unresolved_count": (
                unresolved_count
            ),
        }

    def _identify_observation(
        self,
        observation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve identity for one medication observation.

        Args:
            observation:
                Structured output produced by the Intake Agent.

        Returns:
            Original observation plus identity fields.

        Safety:
            Ambiguous identity remains unresolved.
        """
        medication_name_raw = (
            observation.get(
                "medication_name_raw"
            )
        )

        if not medication_name_raw:
            result = {
                "canonical_name": None,
                "identity_status": (
                    "missing_identity"
                ),
                "identity_confidence": 0.0,
                "identity_reason": (
                    "Observation did not contain a "
                    "medication name."
                ),
                "needs_verification": True,
            }

        else:
            result = resolve_identity(
                medication_name_raw
            )

        identified = {
            **observation,
            **result,
        }

        # Preserve an earlier verification requirement from the Intake
        # Agent. Identity resolution must never erase extraction uncertainty.
        identified[
            "needs_verification"
        ] = bool(
            observation.get(
                "needs_verification",
                False,
            )
            or result[
                "needs_verification"
            ]
        )

        if result[
            "canonical_name"
        ] is None:
            self.record_step(
                AgentStepType.HUMAN_CHECKPOINT,
                "Medication identity requires verification.",
                {
                    "observation_id": (
                        observation.get(
                            "observation_id"
                        )
                    ),
                    "medication_name_raw": (
                        medication_name_raw
                    ),
                    "identity_status": result[
                        "identity_status"
                    ],
                },
            )

        else:
            self.record_step(
                AgentStepType.OUTPUT_CREATED,
                "Medication identity resolved.",
                {
                    "observation_id": (
                        observation.get(
                            "observation_id"
                        )
                    ),
                    "medication_name_raw": (
                        medication_name_raw
                    ),
                    "canonical_name": result[
                        "canonical_name"
                    ],
                },
            )

        return identified
