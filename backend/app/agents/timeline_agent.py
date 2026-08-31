"""
Medication Timeline Agent for MedRecon AI.

Purpose:
    Convert identified medication observations into chronological medication
    event sequences.

Why this agent exists:
    Medication reconciliation depends heavily on time.

    A medication documented on an older prescription may have been changed,
    discontinued, restarted, or replaced in a newer source.

    The Timeline Agent organizes observations so downstream reconciliation can
    reason about sequence rather than treating every source as equally current.

Responsibilities:
    - group observations by medication identity
    - preserve unresolved medication identities
    - sort events chronologically
    - assign event sequence positions
    - identify earliest and latest observations
    - preserve source provenance and evidence
    - expose explicit source status wording

Non-responsibilities:
    - determining the final reconciled medication status
    - resolving conflicts
    - deciding which source is clinically correct
    - screening drug interactions
    - changing medication therapy

Safety:
    Chronology is descriptive.

    The Timeline Agent must not infer a final clinical medication state solely
    because one source is newer. Final interpretation belongs to the
    Reconciliation Agent and later Verification Agent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.agents.base import (
    AgentStepType,
    BaseAgent,
)


def parse_source_date(
    value: str | None,
) -> datetime | None:
    """
    Parse a source date into a datetime.

    Args:
        value:
            Date string, normally in YYYY-MM-DD format.

    Returns:
        Parsed datetime or None.

    Failure behavior:
        Invalid or missing dates are returned as None rather than guessed.

    Why:
        Missing chronology is itself useful uncertainty and should remain
        visible to downstream agents.
    """
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value
        )

    except ValueError:
        return None


def medication_group_key(
    observation: dict[str, Any],
) -> str:
    """
    Determine the grouping key for a medication observation.

    Args:
        observation:
            Identified medication observation.

    Returns:
        Canonical medication name when available.

        Otherwise a stable unresolved identity key based on the raw term.

    Safety:
        An unresolved term is not converted into a guessed medication identity.
    """
    canonical_name = observation.get(
        "canonical_name"
    )

    if canonical_name:
        return canonical_name

    raw_name = observation.get(
        "medication_name_raw",
        "unknown",
    )

    return (
        f"UNRESOLVED::{raw_name}"
    )


def sort_observations(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort medication observations chronologically.

    Observations with valid dates are ordered oldest to newest.

    Missing or invalid dates are placed after dated observations so they remain
    visible but are not silently treated as the newest clinical evidence.
    """
    def sort_key(
        observation: dict[str, Any],
    ) -> tuple[int, datetime]:
        parsed = parse_source_date(
            observation.get(
                "source_date"
            )
        )

        if parsed is None:
            return (
                1,
                datetime.max,
            )

        return (
            0,
            parsed,
        )

    return sorted(
        observations,
        key=sort_key,
    )


class MedicationTimelineAgent(BaseAgent):
    """
    Build chronological medication timelines.

    Input:
        {
            "case_id": "...",
            "identified_observations": [...]
        }

    Output:
        {
            "case_id": "...",
            "timelines": [...],
            "timeline_count": ...
        }

    Each timeline contains:
        medication_key
        canonical_name
        raw_names
        event_count
        earliest_date
        latest_date
        needs_verification
        events

    Failure modes:
        - missing source dates
        - invalid source dates
        - unresolved medication identity
        - duplicate observations

    Retry policy:
        No automatic retries are needed for deterministic ordering.

        Missing dates and unresolved identities are surfaced as uncertainty.
    """

    agent_name = "medication_timeline_agent"

    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build medication timelines from identified observations.

        Args:
            payload:
                Output from the Medication Identity Agent.

        Returns:
            Chronologically grouped medication timelines.

        Raises:
            ValueError:
                If required input structure is missing.
        """
        case_id = payload.get(
            "case_id"
        )

        if not case_id:
            raise ValueError(
                "Medication Timeline Agent requires case_id."
            )

        observations = payload.get(
            "identified_observations"
        )

        if not isinstance(
            observations,
            list,
        ):
            raise ValueError(
                "Medication Timeline Agent requires "
                "identified_observations."
            )

        self.record_step(
            AgentStepType.VALIDATION,
            "Validated identified medication observations.",
            {
                "case_id": case_id,
                "observation_count": len(
                    observations
                ),
            },
        )

        grouped: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        for observation in observations:
            key = medication_group_key(
                observation
            )

            grouped.setdefault(
                key,
                [],
            ).append(
                observation
            )

        timelines: list[
            dict[str, Any]
        ] = []

        for medication_key, group in sorted(
            grouped.items()
        ):
            timeline = self._build_timeline(
                medication_key=medication_key,
                observations=group,
            )

            timelines.append(
                timeline
            )

        self.record_step(
            AgentStepType.DECISION,
            "Medication timelines constructed.",
            {
                "timeline_count": len(
                    timelines
                )
            },
        )

        return {
            "case_id": case_id,
            "timelines": timelines,
            "timeline_count": len(
                timelines
            ),
        }

    def _build_timeline(
        self,
        medication_key: str,
        observations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Build one medication-specific chronological timeline.

        Args:
            medication_key:
                Canonical or unresolved medication grouping key.

            observations:
                Observations associated with that medication identity.

        Returns:
            Structured timeline object.
        """
        ordered = sort_observations(
            observations
        )

        events: list[
            dict[str, Any]
        ] = []

        has_missing_date = False

        for index, observation in enumerate(
            ordered,
            start=1,
        ):
            source_date = observation.get(
                "source_date"
            )

            parsed_date = parse_source_date(
                source_date
            )

            if parsed_date is None:
                has_missing_date = True

            event = {
                "sequence": index,
                "observation_id": (
                    observation.get(
                        "observation_id"
                    )
                ),
                "canonical_name": (
                    observation.get(
                        "canonical_name"
                    )
                ),
                "medication_name_raw": (
                    observation.get(
                        "medication_name_raw"
                    )
                ),
                "dose": observation.get(
                    "dose"
                ),
                "frequency": observation.get(
                    "frequency"
                ),
                "route": observation.get(
                    "route"
                ),
                "status_text": (
                    observation.get(
                        "status_text"
                    )
                ),
                "source_id": observation.get(
                    "source_id"
                ),
                "source_type": (
                    observation.get(
                        "source_type"
                    )
                ),
                "source_date": source_date,
                "evidence_text": (
                    observation.get(
                        "evidence_text"
                    )
                ),
                "identity_status": (
                    observation.get(
                        "identity_status"
                    )
                ),
                "identity_confidence": (
                    observation.get(
                        "identity_confidence"
                    )
                ),
                "extraction_confidence": (
                    observation.get(
                        "extraction_confidence"
                    )
                ),
                "needs_verification": bool(
                    observation.get(
                        "needs_verification",
                        False,
                    )
                    or parsed_date is None
                ),
            }

            events.append(
                event
            )

        dated_events = [
            event
            for event in events
            if parse_source_date(
                event.get(
                    "source_date"
                )
            )
            is not None
        ]

        earliest_date = (
            dated_events[0][
                "source_date"
            ]
            if dated_events
            else None
        )

        latest_date = (
            dated_events[-1][
                "source_date"
            ]
            if dated_events
            else None
        )

        raw_names = sorted(
            {
                event[
                    "medication_name_raw"
                ]
                for event in events
                if event.get(
                    "medication_name_raw"
                )
            }
        )

        canonical_name = next(
            (
                event[
                    "canonical_name"
                ]
                for event in events
                if event.get(
                    "canonical_name"
                )
            ),
            None,
        )

        requires_verification = (
            has_missing_date
            or canonical_name is None
            or any(
                event[
                    "needs_verification"
                ]
                for event in events
            )
        )

        if has_missing_date:
            self.record_step(
                AgentStepType.HUMAN_CHECKPOINT,
                "Medication timeline contains an observation without "
                "a valid source date.",
                {
                    "medication_key": (
                        medication_key
                    )
                },
            )

        if canonical_name is None:
            self.record_step(
                AgentStepType.HUMAN_CHECKPOINT,
                "Timeline contains unresolved medication identity.",
                {
                    "medication_key": (
                        medication_key
                    )
                },
            )

        self.record_step(
            AgentStepType.OUTPUT_CREATED,
            "Medication timeline created.",
            {
                "medication_key": (
                    medication_key
                ),
                "event_count": len(
                    events
                ),
                "earliest_date": (
                    earliest_date
                ),
                "latest_date": (
                    latest_date
                ),
            },
        )

        return {
            "medication_key": (
                medication_key
            ),
            "canonical_name": (
                canonical_name
            ),
            "raw_names": raw_names,
            "event_count": len(
                events
            ),
            "earliest_date": (
                earliest_date
            ),
            "latest_date": (
                latest_date
            ),
            "needs_verification": (
                requires_verification
            ),
            "events": events,
        }
