"""
Medication Reconciliation Agent for MedRecon AI.

Purpose:
    Convert medication timelines into the best-supported reconciled
    medication picture for each case.

Why this agent exists:
    Medication information may change across time and across sources.

    The reconciliation agent determines the best-supported medication state
    while preserving uncertainty and avoiding unsupported assumptions.

Responsibilities:
    - determine current medication state
    - identify explicit medication changes
    - recognize stop-and-restart transitions
    - identify dose, frequency, route, and status conflicts
    - use source provenance when interpreting medication-status disagreement
    - safely carry forward compatible historical attributes
    - avoid carrying historical values across incompatible regimen changes
    - preserve unresolved medication identities
    - produce preliminary discrepancies
    - flag uncertain results for qualified human review
    - preserve supporting evidence

Non-responsibilities:
    - prescribing medication
    - changing medication orders
    - diagnosing patients
    - resolving ambiguous drug identities by guessing
    - screening drug-drug interactions
    - making autonomous clinical decisions

Safety:
    MedRecon produces decision-support findings only.

    Missing or conflicting medication information remains explicit.

    Patient-reported medication status does not automatically override
    conflicting structured medication evidence.

    Qualified human review is required for uncertain or conflicting findings.
"""

from __future__ import annotations

from typing import Any

from app.agents.base import (
    AgentStepType,
    BaseAgent,
)


EXPLICIT_CHANGE_STATUSES = {
    "started",
    "restarted",
    "increased",
    "decreased",
    "changed",
    "discontinued",
}


def latest_event(
    events: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Return the latest chronological medication event.
    """
    if not events:
        return None

    return events[-1]


def latest_non_null(
    events: list[dict[str, Any]],
    field: str,
) -> Any:
    """
    Return the most recent documented non-null value.

    Safety:
        Only documented evidence is carried forward.
        Values are never invented.
    """
    for event in reversed(events):
        value = event.get(field)

        if value is not None:
            return value

    return None


def unique_non_null_values(
    events: list[dict[str, Any]],
    field: str,
) -> list[Any]:
    """
    Return unique documented values for one medication attribute.
    """
    values: list[Any] = []

    for event in events:
        value = event.get(field)

        if (
            value is not None
            and value not in values
        ):
            values.append(value)

    return values


def has_stop_then_start_transition(
    events: list[dict[str, Any]],
) -> bool:
    """
    Detect whether a medication is explicitly stopped and then started again.
    """
    seen_stop = False

    for event in events:
        status = event.get("status_text")

        if status == "discontinued":
            seen_stop = True

        elif (
            seen_stop
            and status
            in {
                "started",
                "restarted",
            }
        ):
            return True

    return False


def latest_started_event(
    events: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Return the latest explicit start or restart event.
    """
    for event in reversed(events):
        if event.get("status_text") in {
            "started",
            "restarted",
        }:
            return event

    return None


def latest_explicit_change_event(
    events: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Return the latest event that explicitly changes the medication regimen.

    A change event may be followed by a confirmation event such as:

        Change Metformin from once daily to twice daily.
        Continue Metformin twice daily.

    Looking only at the final event would lose the fact that an explicit
    transition occurred.
    """
    for event in reversed(events):
        if event.get("status_text") in {
            "increased",
            "decreased",
            "changed",
        }:
            return event

    return None


def has_patient_report_status_conflict(
    events: list[dict[str, Any]],
) -> bool:
    """
    Detect disagreement between patient-reported discontinuation and
    structured evidence supporting an active regimen.

    Example:
        Prescription:
            Losartan 50 mg orally once daily.

        Patient report:
            Patient reports Losartan was stopped.

    This should remain a status conflict because the patient report and the
    structured medication source disagree.

    Safety:
        This rule uses explicit source provenance rather than guessing from
        wording alone.
    """
    patient_report_discontinued = False
    active_structured_evidence = False

    for event in events:
        source_type = (
            event.get("source_type")
            or ""
        ).lower()

        status = event.get("status_text")

        has_regimen_information = any(
            event.get(field) is not None
            for field in (
                "dose",
                "frequency",
                "route",
            )
        )

        if (
            source_type == "patient_report"
            and status == "discontinued"
        ):
            patient_report_discontinued = True

        if (
            source_type != "patient_report"
            and status != "discontinued"
            and has_regimen_information
        ):
            active_structured_evidence = True

    return (
        patient_report_discontinued
        and active_structured_evidence
    )


def infer_reconciled_status(
    events: list[dict[str, Any]],
) -> str:
    """
    Infer the medication's preliminary reconciled status.

    Rules:
        patient-report discontinuation conflicting with active structured
        evidence
            -> conflicting

        stop followed by start/restart
            -> changed

        latest discontinued
            -> discontinued

        latest started/restarted
            -> recently_added

        latest increased/decreased/changed
            -> changed

        explicit change followed by confirmation
            -> changed

        otherwise
            -> current
    """
    if has_patient_report_status_conflict(
        events
    ):
        return "conflicting"

    if has_stop_then_start_transition(
        events
    ):
        return "changed"

    latest = latest_event(
        events
    )

    if latest is None:
        return "uncertain"

    status_text = latest.get(
        "status_text"
    )

    if status_text == "discontinued":
        return "discontinued"

    if status_text in {
        "started",
        "restarted",
    }:
        return "recently_added"

    if status_text in {
        "increased",
        "decreased",
        "changed",
    }:
        return "changed"

    change_event = (
        latest_explicit_change_event(
            events
        )
    )

    if change_event is not None:
        return "changed"

    return "current"


def explicit_change_explains_attribute(
    events: list[dict[str, Any]],
    field: str,
) -> bool:
    """
    Determine whether an explicit medication transition explains multiple
    documented values for a specific attribute.

    Important:
        A true regimen change may be followed by a later confirmation event.

        Example:
            once daily
            -> explicitly changed to twice daily
            -> continued twice daily

        This should not be treated as a frequency conflict.

    Safety:
        The changed event must document the attribute being evaluated, and
        the latest documented value must agree with that changed value.
    """
    if not events:
        return False

    if has_stop_then_start_transition(
        events
    ):
        return True

    latest = latest_event(
        events
    )

    if latest is None:
        return False

    latest_status = latest.get(
        "status_text"
    )

    if latest_status == "discontinued":
        return True

    if latest_status in {
        "started",
        "restarted",
    }:
        return True

    latest_value = latest_non_null(
        events,
        field,
    )

    for event in reversed(
        events
    ):
        status = event.get(
            "status_text"
        )

        changed_value = event.get(
            field
        )

        if changed_value is None:
            continue

        if (
            field == "dose"
            and status
            in {
                "increased",
                "decreased",
                "changed",
            }
        ):
            return (
                changed_value
                == latest_value
            )

        if (
            field
            in {
                "frequency",
                "route",
            }
            and status == "changed"
        ):
            return (
                changed_value
                == latest_value
            )

    return False


def reconcile_transition_attributes(
    events: list[dict[str, Any]],
) -> tuple[
    Any,
    Any,
    Any,
]:
    """
    Determine dose, frequency, and route during an explicit stop/start
    transition.

    Strategy:
        When the same medication is stopped and then restarted, prioritize
        attributes documented in the new regimen.

    Crucial safety rule:
        Do not automatically carry an old dose across a route change.
    """
    start_event = latest_started_event(
        events
    )

    if start_event is None:
        return (
            latest_non_null(
                events,
                "dose",
            ),
            latest_non_null(
                events,
                "frequency",
            ),
            latest_non_null(
                events,
                "route",
            ),
        )

    new_dose = start_event.get(
        "dose"
    )

    new_frequency = start_event.get(
        "frequency"
    )

    new_route = start_event.get(
        "route"
    )

    previous_events = [
        event
        for event in events
        if event is not start_event
    ]

    previous_route = latest_non_null(
        previous_events,
        "route",
    )

    route_changed = (
        new_route is not None
        and previous_route is not None
        and new_route != previous_route
    )

    if route_changed:
        dose = new_dose

    else:
        dose = (
            new_dose
            if new_dose is not None
            else latest_non_null(
                previous_events,
                "dose",
            )
        )

    frequency = (
        new_frequency
        if new_frequency is not None
        else latest_non_null(
            previous_events,
            "frequency",
        )
    )

    route = (
        new_route
        if new_route is not None
        else latest_non_null(
            previous_events,
            "route",
        )
    )

    return (
        dose,
        frequency,
        route,
    )


class MedicationReconciliationAgent(
    BaseAgent
):
    """
    Reconcile medication timelines into best-supported medication states.
    """

    agent_name = (
        "Medication Reconciliation Agent"
    )

    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Reconcile all medication timelines for one case.
        """
        case_id = payload.get(
            "case_id"
        )

        timelines = payload.get(
            "timelines"
        )

        if not case_id:
            raise ValueError(
                "Reconciliation Agent requires case_id."
            )

        if timelines is None:
            raise ValueError(
                "Reconciliation Agent requires timelines."
            )

        self.record_step(
            AgentStepType.VALIDATION,
            "Validated reconciliation input.",
            {
                "case_id": case_id,
                "timeline_count": len(
                    timelines
                ),
            },
        )

        reconciled_medications: list[
            dict[str, Any]
        ] = []

        discrepancies: list[
            dict[str, Any]
        ] = []

        for timeline in timelines:
            (
                reconciled,
                timeline_discrepancies,
            ) = self._reconcile_timeline(
                case_id=case_id,
                timeline=timeline,
            )

            reconciled_medications.append(
                reconciled
            )

            discrepancies.extend(
                timeline_discrepancies
            )

        self.record_step(
            AgentStepType.OUTPUT_CREATED,
            "Created reconciled medication picture.",
            {
                "case_id": case_id,
                "reconciled_count": len(
                    reconciled_medications
                ),
                "discrepancy_count": len(
                    discrepancies
                ),
            },
        )

        return {
            "case_id": case_id,
            "reconciled_medications": (
                reconciled_medications
            ),
            "discrepancies": discrepancies,
            "reconciled_count": len(
                reconciled_medications
            ),
        }

    def _reconcile_timeline(
        self,
        case_id: str,
        timeline: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        list[dict[str, Any]],
    ]:
        """
        Reconcile one medication timeline.

        Safety principles:
            - use explicit newer evidence
            - preserve meaningful source disagreement
            - do not guess conflicting values
            - preserve documented medication transitions
            - do not carry incompatible historical attributes into a new
              regimen
            - preserve unresolved identity
        """
        events = timeline.get(
            "events",
            [],
        )

        canonical_name = timeline.get(
            "canonical_name"
        )

        raw_names = timeline.get(
            "raw_names",
            [],
        )

        if canonical_name:
            medication_name = (
                canonical_name
            )

        elif raw_names:
            medication_name = str(
                raw_names[0]
            ).upper()

        else:
            medication_name = (
                "Unknown medication"
            )

        transition = (
            has_stop_then_start_transition(
                events
            )
        )

        status_source_conflict = (
            has_patient_report_status_conflict(
                events
            )
        )

        if transition:
            (
                dose,
                frequency,
                route,
            ) = reconcile_transition_attributes(
                events
            )

        else:
            dose = latest_non_null(
                events,
                "dose",
            )

            frequency = latest_non_null(
                events,
                "frequency",
            )

            route = latest_non_null(
                events,
                "route",
            )

        status = infer_reconciled_status(
            events
        )

        dose_values = (
            unique_non_null_values(
                events,
                "dose",
            )
        )

        frequency_values = (
            unique_non_null_values(
                events,
                "frequency",
            )
        )

        route_values = (
            unique_non_null_values(
                events,
                "route",
            )
        )

        timeline_discrepancies: list[
            dict[str, Any]
        ] = []

        #
        # Status conflict
        #
        # Patient-reported discontinuation does not automatically override
        # active structured medication evidence.
        #
        if status_source_conflict:
            status = "conflicting"

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "status_conflict"
                    ),
                    severity="medium",
                    description=(
                        "Medication status differs across "
                        "sources. A patient-reported "
                        "discontinuation conflicts with "
                        "structured evidence supporting an "
                        "active medication regimen."
                    ),
                    events=events,
                )
            )

        #
        # Dose conflict
        #
        if (
            len(dose_values) > 1
            and not explicit_change_explains_attribute(
                events,
                "dose",
            )
        ):
            dose = None
            status = "conflicting"

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "dose_conflict"
                    ),
                    severity="medium",
                    description=(
                        "Multiple conflicting medication doses "
                        "are documented without a clear explicit "
                        "dose transition."
                    ),
                    events=events,
                )
            )

        #
        # Frequency conflict
        #
        if (
            len(frequency_values) > 1
            and not explicit_change_explains_attribute(
                events,
                "frequency",
            )
        ):
            frequency = None
            status = "conflicting"

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "frequency_conflict"
                    ),
                    severity="medium",
                    description=(
                        "Multiple conflicting medication "
                        "frequencies are documented without a "
                        "clear explicit frequency transition."
                    ),
                    events=events,
                )
            )

        #
        # Route conflict
        #
        if (
            len(route_values) > 1
            and not explicit_change_explains_attribute(
                events,
                "route",
            )
        ):
            route = None
            status = "conflicting"

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "route_conflict"
                    ),
                    severity="medium",
                    description=(
                        "Multiple conflicting medication routes "
                        "are documented without a clear explicit "
                        "route transition."
                    ),
                    events=events,
                )
            )

        #
        # Unresolved medication identity
        #
        if canonical_name is None:
            status = "uncertain"

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "missing_information"
                    ),
                    severity="medium",
                    description=(
                        "Medication identity could not be "
                        "resolved safely and requires "
                        "verification."
                    ),
                    events=events,
                )
            )

        #
        # Missing information
        #
        if (
            status == "current"
            and (
                dose is None
                or frequency is None
            )
        ):
            status = "uncertain"

            missing_fields: list[
                str
            ] = []

            if dose is None:
                missing_fields.append(
                    "dose"
                )

            if frequency is None:
                missing_fields.append(
                    "frequency"
                )

            timeline_discrepancies.append(
                self._create_discrepancy(
                    medication_name=(
                        medication_name
                    ),
                    discrepancy_type=(
                        "missing_information"
                    ),
                    severity="low",
                    description=(
                        "Current medication information is "
                        "incomplete. Missing: "
                        + ", ".join(
                            missing_fields
                        )
                        + "."
                    ),
                    events=events,
                )
            )

        #
        # Determine human-review requirement.
        #
        needs_verification = (
            status
            in {
                "conflicting",
                "uncertain",
            }
            or canonical_name is None
        )

        supporting_evidence = [
            {
                "source_id": event.get(
                    "source_id"
                ),
                "source_type": event.get(
                    "source_type"
                ),
                "source_date": event.get(
                    "source_date"
                ),
                "evidence_text": event.get(
                    "evidence_text"
                ),
            }
            for event in events
        ]

        reconciled = {
            "case_id": case_id,
            "medication_name": (
                medication_name
            ),
            "dose": dose,
            "frequency": frequency,
            "route": route,
            "status": status,
            "needs_verification": (
                needs_verification
            ),
            "supporting_evidence": (
                supporting_evidence
            ),
        }

        self.record_step(
            AgentStepType.DECISION,
            "Reconciled medication timeline.",
            {
                "medication_name": (
                    medication_name
                ),
                "dose": dose,
                "frequency": frequency,
                "route": route,
                "status": status,
                "stop_start_transition": (
                    transition
                ),
                "status_source_conflict": (
                    status_source_conflict
                ),
                "needs_verification": (
                    needs_verification
                ),
            },
        )

        if needs_verification:
            self.record_step(
                AgentStepType.HUMAN_CHECKPOINT,
                (
                    "Medication requires qualified "
                    "human verification."
                ),
                {
                    "medication_name": (
                        medication_name
                    ),
                    "status": status,
                },
            )

        return (
            reconciled,
            timeline_discrepancies,
        )

    def _create_discrepancy(
        self,
        medication_name: str,
        discrepancy_type: str,
        severity: str,
        description: str,
        events: list[
            dict[str, Any]
        ],
    ) -> dict[str, Any]:
        """
        Create an evidence-backed preliminary discrepancy.

        Findings remain unverified until processed by the future
        Verification Agent or qualified human reviewer.
        """
        evidence = [
            {
                "source_id": event.get(
                    "source_id"
                ),
                "source_type": event.get(
                    "source_type"
                ),
                "source_date": event.get(
                    "source_date"
                ),
                "evidence_text": event.get(
                    "evidence_text"
                ),
            }
            for event in events
        ]

        discrepancy = {
            "medication_name": (
                medication_name
            ),
            "type": (
                discrepancy_type
            ),
            "severity": severity,
            "description": (
                description
            ),
            "verification_status": (
                "unverified"
            ),
            "evidence": evidence,
        }

        self.record_step(
            AgentStepType.OUTPUT_CREATED,
            "Created preliminary medication discrepancy.",
            {
                "medication_name": (
                    medication_name
                ),
                "type": (
                    discrepancy_type
                ),
                "severity": (
                    severity
                ),
            },
        )

        return discrepancy