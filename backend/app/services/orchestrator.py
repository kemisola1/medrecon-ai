"""
MedRecon AI agent pipeline orchestrator.

Purpose:
    Run specialized medication-reconciliation agents in the correct order
    and combine their outputs into one case-level result.

Current V2 pipeline:
    Raw case
        ->
    Intake & Extraction Agent
        ->
    Medication Identity Agent
        ->
    Medication Timeline Agent
        ->
    Medication Reconciliation Agent

Why this service exists:
    Individual agents should remain narrow and independently testable.

    The orchestrator coordinates them without moving specialized reasoning
    into one monolithic function.

Responsibilities:
    - execute agents in sequence
    - pass structured outputs between agents
    - stop safely when an agent fails
    - preserve agent trajectories
    - expose final reconciled medications and discrepancies
    - provide pipeline-level execution metadata

Non-responsibilities:
    - changing medication therapy
    - hiding agent failures
    - modifying ground truth
    - performing evaluation
    - screening drug-drug interactions at this stage

Safety:
    The pipeline produces decision-support output only.

    Consequential medication decisions remain subject to qualified human
    review.

V2 changes:
    - improved extraction of explicit medication transitions
    - preserves repeated mentions of the same medication within a source
    - improves dose-change handling
    - improves route-change handling
    - avoids carrying incompatible historical attributes into a changed
      medication regimen
    - preserves unresolved medication identities for human verification
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.agents.base import (
    AgentExecutionStatus,
    AgentResult,
)
from app.agents.identity_agent import (
    MedicationIdentityAgent,
)
from app.agents.intake_agent import (
    IntakeExtractionAgent,
)
from app.agents.reconciliation_agent import (
    MedicationReconciliationAgent,
)
from app.agents.timeline_agent import (
    MedicationTimelineAgent,
)


class MedReconOrchestrator:
    """
    Coordinate the MedRecon medication reconciliation pipeline.

    Current V2 agents:
        1. IntakeExtractionAgent
        2. MedicationIdentityAgent
        3. MedicationTimelineAgent
        4. MedicationReconciliationAgent

    Future agents can be inserted after reconciliation:
        Discrepancy Agent
        Interaction Agent
        Verification Agent
        Prioritization Agent
    """

    def __init__(self) -> None:
        """
        Create pipeline agent instances.
        """
        self.intake_agent = (
            IntakeExtractionAgent()
        )

        self.identity_agent = (
            MedicationIdentityAgent()
        )

        self.timeline_agent = (
            MedicationTimelineAgent()
        )

        self.reconciliation_agent = (
            MedicationReconciliationAgent()
        )

    def _serialize_agent_result(
        self,
        result: AgentResult,
    ) -> dict[str, Any]:
        """
        Convert an AgentResult into JSON-safe trajectory data.

        Args:
            result:
                Completed or failed agent execution.

        Returns:
            Serializable agent-run record.

        Important:
            Only observable trajectory information is stored.

            Hidden chain-of-thought is never recorded.
        """
        return result.model_dump(
            mode="json"
        )

    def _ensure_success(
        self,
        result: AgentResult,
    ) -> None:
        """
        Ensure an agent completed successfully.

        Args:
            result:
                Agent execution result.

        Raises:
            RuntimeError:
                When an agent does not complete successfully.

        Why:
            A downstream agent should never silently continue using failed
            or incomplete upstream output.
        """
        if (
            result.status
            != AgentExecutionStatus.COMPLETED
        ):
            raise RuntimeError(
                f"{result.agent_name} failed: "
                f"{result.error}"
            )

    def run_case(
        self,
        case: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run the MedRecon V2 pipeline for one synthetic case.

        Args:
            case:
                Raw synthetic medication-reconciliation case.

        Returns:
            Case-level pipeline result containing:
                medications
                discrepancies
                interactions
                agent trajectories
                execution metadata

        Failure behavior:
            If any agent fails, execution stops immediately and a structured
            failed result is returned.

        Safety:
            The returned medication picture is decision-support information,
            not an autonomous clinical action.
        """
        case_id = case.get(
            "case_id"
        )

        if not case_id:
            raise ValueError(
                "MedRecon pipeline requires case_id."
            )

        pipeline_run_id = str(
            uuid4()
        )

        started_at = datetime.now(
            timezone.utc
        )

        agent_runs: list[
            dict[str, Any]
        ] = []

        try:
            # -------------------------------------------------------------
            # 1. Intake & Extraction
            # -------------------------------------------------------------
            intake_result = (
                self.intake_agent.run(
                    case
                )
            )

            agent_runs.append(
                self._serialize_agent_result(
                    intake_result
                )
            )

            self._ensure_success(
                intake_result
            )

            # -------------------------------------------------------------
            # 2. Medication Identity
            # -------------------------------------------------------------
            identity_result = (
                self.identity_agent.run(
                    intake_result.output
                )
            )

            agent_runs.append(
                self._serialize_agent_result(
                    identity_result
                )
            )

            self._ensure_success(
                identity_result
            )

            # -------------------------------------------------------------
            # 3. Medication Timeline
            # -------------------------------------------------------------
            timeline_result = (
                self.timeline_agent.run(
                    identity_result.output
                )
            )

            agent_runs.append(
                self._serialize_agent_result(
                    timeline_result
                )
            )

            self._ensure_success(
                timeline_result
            )

            # -------------------------------------------------------------
            # 4. Medication Reconciliation
            # -------------------------------------------------------------
            reconciliation_result = (
                self.reconciliation_agent.run(
                    timeline_result.output
                )
            )

            agent_runs.append(
                self._serialize_agent_result(
                    reconciliation_result
                )
            )

            self._ensure_success(
                reconciliation_result
            )

            completed_at = datetime.now(
                timezone.utc
            )

            return {
                "pipeline_run_id": (
                    pipeline_run_id
                ),
                "case_id": (
                    case_id
                ),
                "status": (
                    "completed"
                ),
                "medications": (
                    reconciliation_result.output.get(
                        "reconciled_medications",
                        [],
                    )
                ),
                "discrepancies": (
                    reconciliation_result.output.get(
                        "discrepancies",
                        [],
                    )
                ),
                "interactions": [],
                "agent_runs": (
                    agent_runs
                ),
                "started_at": (
                    started_at.isoformat()
                ),
                "completed_at": (
                    completed_at.isoformat()
                ),
                "pipeline_version": (
                    "V2"
                ),
                "notes": [
                    (
                        "V2 preserves repeated medication "
                        "mentions within a source so explicit "
                        "medication transitions can be "
                        "reconstructed."
                    ),
                    (
                        "V2 improves explicit dose, frequency, "
                        "and route transition handling."
                    ),
                    (
                        "V2 avoids carrying incompatible "
                        "historical attributes into a changed "
                        "medication regimen."
                    ),
                    (
                        "Ambiguous medication identities remain "
                        "unresolved and are flagged for "
                        "verification rather than guessed."
                    ),
                    (
                        "Interaction screening and formal "
                        "verification agents are not included "
                        "yet."
                    ),
                ],
            }

        except Exception as exc:
            completed_at = datetime.now(
                timezone.utc
            )

            return {
                "pipeline_run_id": (
                    pipeline_run_id
                ),
                "case_id": (
                    case_id
                ),
                "status": (
                    "failed"
                ),
                "medications": [],
                "discrepancies": [],
                "interactions": [],
                "agent_runs": (
                    agent_runs
                ),
                "error": str(
                    exc
                ),
                "started_at": (
                    started_at.isoformat()
                ),
                "completed_at": (
                    completed_at.isoformat()
                ),
                "pipeline_version": (
                    "V2"
                ),
            }