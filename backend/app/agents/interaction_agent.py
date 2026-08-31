"""
Medication Interaction Agent for MedRecon AI.

Purpose:
    Screen the reconciled medication picture for potential drug-drug
    interactions using a designated deterministic knowledge source.

Core principle:
    Reconcile first. Alert second.

Why this agent exists:
    Interaction screening is only meaningful after MedRecon has determined
    which medications are best supported as current, recently added, changed,
    or otherwise relevant to the active medication picture.

Responsibilities:
    - receive reconciled medications
    - select medications appropriate for interaction screening
    - query the approved interaction knowledge base
    - identify supported medication pairs
    - preserve knowledge-source evidence
    - produce potential interaction findings
    - flag consequential findings for qualified human review

Non-responsibilities:
    - guessing interactions from model memory
    - prescribing medication
    - discontinuing medication
    - changing doses
    - diagnosing patients
    - autonomously resolving clinical risk

Safety:
    Interaction findings are decision-support information only.

    Only interactions present in the designated knowledge base are returned.

    Qualified clinician or pharmacist review is required before any
    consequential medication decision.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.agents.base import (
    AgentStepType,
    BaseAgent,
)


SCREENABLE_STATUSES = {
    "current",
    "recently_added",
    "changed",
}


def normalize_medication_name(
    value: str,
) -> str:
    """
    Normalize medication names for deterministic comparison.
    """
    return (
        value.strip()
        .lower()
        .replace("–", "-")
        .replace("—", "-")
    )


def interaction_pair_key(
    drug_a: str,
    drug_b: str,
) -> tuple[str, str]:
    """
    Create an order-independent medication-pair key.
    """
    normalized = sorted(
        [
            normalize_medication_name(
                drug_a
            ),
            normalize_medication_name(
                drug_b
            ),
        ]
    )

    return (
        normalized[0],
        normalized[1],
    )


class MedicationInteractionAgent(
    BaseAgent
):
    """
    Screen reconciled medications using an approved interaction knowledge
    base.
    """

    agent_name = (
        "Medication Interaction Agent"
    )

    def __init__(
        self,
        knowledge_base_path: str | Path | None = None,
    ) -> None:
        super().__init__()

        if knowledge_base_path is None:
            project_root = (
                Path(__file__)
                .resolve()
                .parents[3]
            )

            knowledge_base_path = (
                project_root
                / "data"
                / "medications"
                / "interaction_knowledge.json"
            )

        self.knowledge_base_path = Path(
            knowledge_base_path
        )

        self.knowledge_base = (
            self._load_knowledge_base()
        )

        self.interaction_index = (
            self._build_interaction_index()
        )

    def _load_knowledge_base(
        self,
    ) -> dict[str, Any]:
        """
        Load the designated interaction knowledge source.
        """
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                "Interaction knowledge base not found: "
                f"{self.knowledge_base_path}"
            )

        with self.knowledge_base_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(
                file
            )

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "Interaction knowledge base must be a JSON object."
            )

        interactions = payload.get(
            "interactions"
        )

        if not isinstance(
            interactions,
            list,
        ):
            raise ValueError(
                "Interaction knowledge base requires an interactions list."
            )

        return payload

    def _build_interaction_index(
        self,
    ) -> dict[
        tuple[str, str],
        dict[str, Any],
    ]:
        """
        Build a deterministic lookup index for interaction pairs.
        """
        index: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        for interaction in self.knowledge_base.get(
            "interactions",
            [],
        ):
            drug_a = interaction.get(
                "drug_a"
            )

            drug_b = interaction.get(
                "drug_b"
            )

            if (
                not drug_a
                or not drug_b
            ):
                continue

            key = interaction_pair_key(
                drug_a,
                drug_b,
            )

            index[key] = interaction

        return index

    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Screen the reconciled medication picture for supported interactions.
        """
        case_id = payload.get(
            "case_id"
        )

        medications = payload.get(
            "medications"
        )

        if not case_id:
            raise ValueError(
                "Interaction Agent requires case_id."
            )

        if medications is None:
            raise ValueError(
                "Interaction Agent requires medications."
            )

        if not isinstance(
            medications,
            list,
        ):
            raise ValueError(
                "Interaction Agent medications must be a list."
            )

        self.record_step(
            AgentStepType.VALIDATION,
            "Validated reconciled medications for interaction screening.",
            {
                "case_id": case_id,
                "medication_count": len(
                    medications
                ),
                "knowledge_base_version": (
                    self.knowledge_base.get(
                        "version"
                    )
                ),
            },
        )

        screenable_medications = [
            medication
            for medication in medications
            if medication.get(
                "status"
            )
            in SCREENABLE_STATUSES
        ]

        self.record_step(
            AgentStepType.DECISION,
            (
                "Selected reconciled medications eligible "
                "for interaction screening."
            ),
            {
                "case_id": case_id,
                "screenable_count": len(
                    screenable_medications
                ),
                "screenable_medications": [
                    medication.get(
                        "medication_name"
                    )
                    for medication
                    in screenable_medications
                ],
            },
        )

        interactions: list[
            dict[str, Any]
        ] = []

        for left_index in range(
            len(
                screenable_medications
            )
        ):
            for right_index in range(
                left_index + 1,
                len(
                    screenable_medications
                ),
            ):
                left = (
                    screenable_medications[
                        left_index
                    ]
                )

                right = (
                    screenable_medications[
                        right_index
                    ]
                )

                left_name = left.get(
                    "medication_name"
                )

                right_name = right.get(
                    "medication_name"
                )

                if (
                    not left_name
                    or not right_name
                ):
                    continue

                pair_key = (
                    interaction_pair_key(
                        left_name,
                        right_name,
                    )
                )

                self.record_step(
                    AgentStepType.TOOL_CALL,
                    (
                        "Queried approved interaction "
                        "knowledge base."
                    ),
                    {
                        "drug_a": (
                            left_name
                        ),
                        "drug_b": (
                            right_name
                        ),
                        "knowledge_base": (
                            self.knowledge_base.get(
                                "knowledge_base_name"
                            )
                        ),
                    },
                )

                interaction = (
                    self.interaction_index.get(
                        pair_key
                    )
                )

                self.record_step(
                    AgentStepType.TOOL_RESULT,
                    (
                        "Interaction knowledge lookup "
                        "completed."
                    ),
                    {
                        "drug_a": (
                            left_name
                        ),
                        "drug_b": (
                            right_name
                        ),
                        "interaction_found": (
                            interaction
                            is not None
                        ),
                    },
                )

                if interaction is None:
                    continue

                finding = (
                    self._create_interaction_finding(
                        case_id=case_id,
                        interaction=interaction,
                        medication_a=left,
                        medication_b=right,
                    )
                )

                interactions.append(
                    finding
                )

                self.record_step(
                    AgentStepType.OUTPUT_CREATED,
                    (
                        "Created knowledge-supported "
                        "interaction finding."
                    ),
                    {
                        "drug_a": (
                            finding[
                                "drug_a"
                            ]
                        ),
                        "drug_b": (
                            finding[
                                "drug_b"
                            ]
                        ),
                        "severity": (
                            finding[
                                "severity"
                            ]
                        ),
                    },
                )

                self.record_step(
                    AgentStepType.HUMAN_CHECKPOINT,
                    (
                        "Potential medication interaction "
                        "requires qualified clinical review."
                    ),
                    {
                        "drug_a": (
                            finding[
                                "drug_a"
                            ]
                        ),
                        "drug_b": (
                            finding[
                                "drug_b"
                            ]
                        ),
                        "severity": (
                            finding[
                                "severity"
                            ]
                        ),
                    },
                )

        self.record_step(
            AgentStepType.DECISION,
            (
                "Completed deterministic interaction "
                "screening."
            ),
            {
                "case_id": case_id,
                "interaction_count": len(
                    interactions
                ),
            },
        )

        return {
            "case_id": case_id,
            "interactions": interactions,
            "interaction_count": len(
                interactions
            ),
            "knowledge_base": {
                "name": (
                    self.knowledge_base.get(
                        "knowledge_base_name"
                    )
                ),
                "version": (
                    self.knowledge_base.get(
                        "version"
                    )
                ),
            },
        }

    def _create_interaction_finding(
        self,
        case_id: str,
        interaction: dict[str, Any],
        medication_a: dict[str, Any],
        medication_b: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create an evidence-backed potential interaction finding.
        """
        source = interaction.get(
            "source",
            {},
        )

        return {
            "case_id": case_id,
            "drug_a": (
                medication_a.get(
                    "medication_name"
                )
            ),
            "drug_b": (
                medication_b.get(
                    "medication_name"
                )
            ),
            "type": interaction.get(
                "interaction_type",
                "drug_drug_interaction",
            ),
            "severity": interaction.get(
                "severity"
            ),
            "summary": interaction.get(
                "summary"
            ),
            "mechanism": interaction.get(
                "mechanism"
            ),
            "recommended_action": (
                interaction.get(
                    "recommended_action"
                )
            ),
            "verification_status": (
                interaction.get(
                    "verification_status",
                    "knowledge_base_supported",
                )
            ),
            "needs_human_review": True,
            "knowledge_source": {
                "source_type": (
                    source.get(
                        "source_type"
                    )
                ),
                "source_name": (
                    source.get(
                        "source_name"
                    )
                ),
                "version": (
                    source.get(
                        "version"
                    )
                ),
            },
            "medication_evidence": {
                "drug_a": (
                    medication_a.get(
                        "supporting_evidence",
                        [],
                    )
                ),
                "drug_b": (
                    medication_b.get(
                        "supporting_evidence",
                        [],
                    )
                ),
            },
        }