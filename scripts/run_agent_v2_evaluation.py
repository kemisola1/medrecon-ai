"""
Evaluate the MedRecon AI V2 agent pipeline against synthetic ground truth.

Purpose:
    Measure whether the improved V2 agentic medication reconciliation
    workflow improves over the frozen V0 deterministic baseline and the
    preserved V1 agent pipeline.

Primary metric:
    Medication Reconciliation F1.

    A medication prediction counts as a strict reconciliation match only
    when all of the following match the ground truth:
        - medication identity
        - dose
        - frequency
        - route
        - status

Secondary metrics:
    - Medication Identity F1
    - Dose Accuracy
    - Frequency Accuracy
    - Route Accuracy
    - Status Accuracy
    - Discrepancy F1
    - Interaction F1

Important:
    This evaluator uses the same comparison rules as the V0 baseline and
    V1 agent evaluators so all versions remain directly comparable.

    Ground truth is used only during evaluation. It is never provided to
    the MedRecon agents while they process cases.

Safety:
    This script evaluates synthetic hackathon data only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent


GROUND_TRUTH_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "ground_truth"
)


AGENT_RESULTS_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "agent_v2_results.json"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "agent_v2_metrics.json"
)


V0_RECONCILIATION_F1 = 0.6000
V1_RECONCILIATION_F1 = 0.5902


def load_json(
    path: Path,
) -> Any:
    """
    Load JSON data from disk.

    Args:
        path:
            Path to the JSON file.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError:
            If the requested file does not exist.

        json.JSONDecodeError:
            If the file contains invalid JSON.
    """
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(
            file
        )


def save_json(
    path: Path,
    payload: Any,
) -> None:
    """
    Save evaluation output as formatted JSON.

    Args:
        path:
            Destination file path.

        payload:
            JSON-serializable evaluation result.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )


def normalize_value(
    value: Any,
) -> str | None:
    """
    Normalize values before comparison.

    Why:
        Harmless differences such as capitalization or surrounding
        whitespace should not count as reconciliation errors.

    Args:
        value:
            Value to normalize.

    Returns:
        Lowercase whitespace-normalized string or None.
    """
    if value is None:
        return None

    normalized = " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )

    return normalized or None


def medication_identity_key(
    medication: dict[str, Any],
) -> str | None:
    """
    Return the normalized medication identity.
    """
    return normalize_value(
        medication.get(
            "medication_name"
        )
    )


def reconciliation_key(
    medication: dict[str, Any],
) -> tuple[Any, ...]:
    """
    Build the strict medication reconciliation comparison key.

    A correct reconciliation requires an exact normalized match for:
        medication identity
        dose
        frequency
        route
        status
    """
    return (
        normalize_value(
            medication.get(
                "medication_name"
            )
        ),
        normalize_value(
            medication.get(
                "dose"
            )
        ),
        normalize_value(
            medication.get(
                "frequency"
            )
        ),
        normalize_value(
            medication.get(
                "route"
            )
        ),
        normalize_value(
            medication.get(
                "status"
            )
        ),
    )


def discrepancy_key(
    discrepancy: dict[str, Any],
) -> tuple[Any, ...]:
    """
    Build a comparison key for medication discrepancies.

    Detection is evaluated by:
        medication identity
        discrepancy type

    Severity is intentionally excluded from the detection match.
    """
    return (
        normalize_value(
            discrepancy.get(
                "medication_name"
            )
        ),
        normalize_value(
            discrepancy.get(
                "type"
            )
        ),
    )


def interaction_key(
    interaction: dict[str, Any],
) -> tuple[str, str]:
    """
    Build an order-independent drug interaction key.

    Example:
        Warfarin + Medication B

    is treated as equivalent to:

        Medication B + Warfarin
    """
    medication_a = (
        normalize_value(
            interaction.get(
                "medication_a"
            )
        )
        or ""
    )

    medication_b = (
        normalize_value(
            interaction.get(
                "medication_b"
            )
        )
        or ""
    )

    pair = sorted(
        [
            medication_a,
            medication_b,
        ]
    )

    return (
        pair[0],
        pair[1],
    )


def precision_recall_f1(
    predicted: set[Any],
    expected: set[Any],
) -> dict[str, float | int]:
    """
    Calculate precision, recall, and F1 for one set-based comparison.

    Args:
        predicted:
            Predictions produced by the V2 pipeline.

        expected:
            Synthetic ground-truth values.

    Returns:
        TP, FP, FN, precision, recall, and F1.

    Empty-set behavior:
        When both sets are empty, the case correctly predicts absence and
        receives perfect case-level scores.
    """
    true_positive = len(
        predicted & expected
    )

    false_positive = len(
        predicted - expected
    )

    false_negative = len(
        expected - predicted
    )

    if (
        not predicted
        and not expected
    ):
        precision = 1.0
        recall = 1.0
        f1 = 1.0

    else:
        precision = (
            true_positive
            / (
                true_positive
                + false_positive
            )
            if (
                true_positive
                + false_positive
            )
            else 0.0
        )

        recall = (
            true_positive
            / (
                true_positive
                + false_negative
            )
            if (
                true_positive
                + false_negative
            )
            else 0.0
        )

        f1 = (
            2
            * precision
            * recall
            / (
                precision
                + recall
            )
            if (
                precision
                + recall
            )
            else 0.0
        )

    return {
        "true_positive": (
            true_positive
        ),
        "false_positive": (
            false_positive
        ),
        "false_negative": (
            false_negative
        ),
        "precision": round(
            precision,
            4,
        ),
        "recall": round(
            recall,
            4,
        ),
        "f1": round(
            f1,
            4,
        ),
    }


def build_medication_map(
    medications: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Build a medication lookup indexed by normalized medication identity.
    """
    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for medication in medications:
        key = medication_identity_key(
            medication
        )

        if key is not None:
            result[
                key
            ] = medication

    return result


def evaluate_attributes(
    predicted_medications: list[dict[str, Any]],
    expected_medications: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Evaluate dose, frequency, route, and status accuracy.

    Attribute comparison is performed only for medication identities found
    in both the prediction and ground truth.
    """
    predicted_map = (
        build_medication_map(
            predicted_medications
        )
    )

    expected_map = (
        build_medication_map(
            expected_medications
        )
    )

    shared_names = (
        set(
            predicted_map
        )
        & set(
            expected_map
        )
    )

    attributes = (
        "dose",
        "frequency",
        "route",
        "status",
    )

    results: dict[
        str,
        dict[str, Any],
    ] = {}

    for attribute in attributes:
        correct = 0
        total = 0

        for medication_name in shared_names:
            predicted_value = (
                normalize_value(
                    predicted_map[
                        medication_name
                    ].get(
                        attribute
                    )
                )
            )

            expected_value = (
                normalize_value(
                    expected_map[
                        medication_name
                    ].get(
                        attribute
                    )
                )
            )

            total += 1

            if (
                predicted_value
                == expected_value
            ):
                correct += 1

        accuracy = (
            correct / total
            if total
            else 0.0
        )

        results[
            attribute
        ] = {
            "correct": correct,
            "total": total,
            "accuracy": round(
                accuracy,
                4,
            ),
        }

    return results


def evaluate_case(
    prediction: dict[str, Any],
    ground_truth: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate one V2 pipeline prediction against one ground-truth case.

    Prediction schema:
        medications
        discrepancies
        interactions

    Ground-truth schema:
        expected_medications
        expected_discrepancies
        expected_interactions
    """
    prediction_case_id = (
        prediction.get(
            "case_id"
        )
    )

    ground_truth_case_id = (
        ground_truth.get(
            "case_id"
        )
    )

    if (
        prediction_case_id
        != ground_truth_case_id
    ):
        raise ValueError(
            "Case ID mismatch during evaluation: "
            f"prediction={prediction_case_id}, "
            f"ground_truth={ground_truth_case_id}"
        )

    predicted_medications = (
        prediction.get(
            "medications",
            [],
        )
    )

    expected_medications = (
        ground_truth.get(
            "expected_medications",
            [],
        )
    )

    predicted_discrepancies = (
        prediction.get(
            "discrepancies",
            [],
        )
    )

    expected_discrepancies = (
        ground_truth.get(
            "expected_discrepancies",
            [],
        )
    )

    predicted_interactions = (
        prediction.get(
            "interactions",
            [],
        )
    )

    expected_interactions = (
        ground_truth.get(
            "expected_interactions",
            [],
        )
    )

    predicted_identity = {
        medication_identity_key(
            medication
        )
        for medication
        in predicted_medications
    }

    expected_identity = {
        medication_identity_key(
            medication
        )
        for medication
        in expected_medications
    }

    predicted_identity.discard(
        None
    )

    expected_identity.discard(
        None
    )

    predicted_reconciliation = {
        reconciliation_key(
            medication
        )
        for medication
        in predicted_medications
    }

    expected_reconciliation = {
        reconciliation_key(
            medication
        )
        for medication
        in expected_medications
    }

    predicted_discrepancy_keys = {
        discrepancy_key(
            discrepancy
        )
        for discrepancy
        in predicted_discrepancies
    }

    expected_discrepancy_keys = {
        discrepancy_key(
            discrepancy
        )
        for discrepancy
        in expected_discrepancies
    }

    predicted_interaction_keys = {
        interaction_key(
            interaction
        )
        for interaction
        in predicted_interactions
    }

    expected_interaction_keys = {
        interaction_key(
            interaction
        )
        for interaction
        in expected_interactions
    }

    return {
        "case_id": (
            prediction_case_id
        ),
        "medication_identity": (
            precision_recall_f1(
                predicted_identity,
                expected_identity,
            )
        ),
        "medication_reconciliation": (
            precision_recall_f1(
                predicted_reconciliation,
                expected_reconciliation,
            )
        ),
        "attributes": (
            evaluate_attributes(
                predicted_medications,
                expected_medications,
            )
        ),
        "discrepancies": (
            precision_recall_f1(
                predicted_discrepancy_keys,
                expected_discrepancy_keys,
            )
        ),
        "interactions": (
            precision_recall_f1(
                predicted_interaction_keys,
                expected_interaction_keys,
            )
        ),
    }


def aggregate_set_metric(
    case_results: list[dict[str, Any]],
    metric_name: str,
) -> dict[str, float | int]:
    """
    Calculate micro-averaged dataset metrics.

    Why micro averaging:
        TP, FP, and FN are summed across all 20 cases before calculating
        precision, recall, and F1.

        This prevents small cases from receiving disproportionate weight.
    """
    true_positive = sum(
        case[
            metric_name
        ][
            "true_positive"
        ]
        for case
        in case_results
    )

    false_positive = sum(
        case[
            metric_name
        ][
            "false_positive"
        ]
        for case
        in case_results
    )

    false_negative = sum(
        case[
            metric_name
        ][
            "false_negative"
        ]
        for case
        in case_results
    )

    precision = (
        true_positive
        / (
            true_positive
            + false_positive
        )
        if (
            true_positive
            + false_positive
        )
        else (
            1.0
            if false_negative == 0
            else 0.0
        )
    )

    recall = (
        true_positive
        / (
            true_positive
            + false_negative
        )
        if (
            true_positive
            + false_negative
        )
        else 1.0
    )

    f1 = (
        2
        * precision
        * recall
        / (
            precision
            + recall
        )
        if (
            precision
            + recall
        )
        else 0.0
    )

    return {
        "true_positive": (
            true_positive
        ),
        "false_positive": (
            false_positive
        ),
        "false_negative": (
            false_negative
        ),
        "precision": round(
            precision,
            4,
        ),
        "recall": round(
            recall,
            4,
        ),
        "f1": round(
            f1,
            4,
        ),
    }


def aggregate_attributes(
    case_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Aggregate medication attribute accuracy across all evaluation cases.
    """
    attributes = (
        "dose",
        "frequency",
        "route",
        "status",
    )

    output: dict[
        str,
        dict[str, Any],
    ] = {}

    for attribute in attributes:
        correct = sum(
            case[
                "attributes"
            ][
                attribute
            ][
                "correct"
            ]
            for case
            in case_results
        )

        total = sum(
            case[
                "attributes"
            ][
                attribute
            ][
                "total"
            ]
            for case
            in case_results
        )

        accuracy = (
            correct / total
            if total
            else 0.0
        )

        output[
            attribute
        ] = {
            "correct": correct,
            "total": total,
            "accuracy": round(
                accuracy,
                4,
            ),
        }

    return output


def load_ground_truth(
    case_id: str,
) -> dict[str, Any]:
    """
    Load the synthetic ground truth associated with one case.

    Args:
        case_id:
            Synthetic case identifier such as SYN-001.

    Returns:
        Ground-truth JSON payload.

    Raises:
        FileNotFoundError:
            If the corresponding ground-truth file does not exist.
    """
    path = (
        GROUND_TRUTH_DIR
        / f"{case_id}.json"
    )

    if not path.exists():
        raise FileNotFoundError(
            "Ground truth not found for "
            f"{case_id}: {path}"
        )

    return load_json(
        path
    )


def main() -> None:
    """
    Evaluate all successful MedRecon V2 pipeline predictions.
    """
    if not AGENT_RESULTS_FILE.exists():
        raise FileNotFoundError(
            "V2 agent results were not found. "
            "Run scripts/run_agent_v2_pipeline.py first."
        )

    agent_payload = load_json(
        AGENT_RESULTS_FILE
    )

    predictions = agent_payload.get(
        "results",
        [],
    )

    if not predictions:
        raise ValueError(
            "The V2 agent results file contains no predictions."
        )

    case_results: list[
        dict[str, Any]
    ] = []

    print(
        f"Evaluating {len(predictions)} "
        "V2 agent cases..."
    )

    for prediction in predictions:
        case_id = prediction.get(
            "case_id"
        )

        if not case_id:
            raise ValueError(
                "Agent prediction is missing case_id."
            )

        if (
            prediction.get(
                "status"
            )
            != "completed"
        ):
            raise ValueError(
                f"Cannot evaluate {case_id}: "
                "pipeline status is not completed."
            )

        ground_truth = load_ground_truth(
            case_id
        )

        result = evaluate_case(
            prediction,
            ground_truth,
        )

        case_results.append(
            result
        )

        reconciliation_f1 = (
            result[
                "medication_reconciliation"
            ][
                "f1"
            ]
        )

        print(
            f"[OK] {case_id} | "
            "reconciliation_f1="
            f"{reconciliation_f1:.4f}"
        )

    summary = {
        "evaluation_name": (
            "MedRecon AI V2 Agent Pipeline"
        ),
        "system_version": (
            "V2"
        ),
        "case_count": len(
            case_results
        ),
        "primary_metric": (
            "medication_reconciliation_f1"
        ),
        "primary_metric_definition": (
            "Micro-averaged F1 where a medication "
            "is correct only when medication identity, "
            "dose, frequency, route, and status all "
            "match synthetic ground truth."
        ),
        "medication_reconciliation": (
            aggregate_set_metric(
                case_results,
                "medication_reconciliation",
            )
        ),
        "medication_identity": (
            aggregate_set_metric(
                case_results,
                "medication_identity",
            )
        ),
        "attributes": (
            aggregate_attributes(
                case_results
            )
        ),
        "discrepancies": (
            aggregate_set_metric(
                case_results,
                "discrepancies",
            )
        ),
        "interactions": (
            aggregate_set_metric(
                case_results,
                "interactions",
            )
        ),
        "comparison_targets": {
            "v0_medication_reconciliation_f1": (
                V0_RECONCILIATION_F1
            ),
            "v1_medication_reconciliation_f1": (
                V1_RECONCILIATION_F1
            ),
        },
        "cases": (
            case_results
        ),
    }

    save_json(
        OUTPUT_FILE,
        summary,
    )

    print()
    print(
        "V2 agent evaluation complete."
    )

    print()
    print(
        "PRIMARY METRIC"
    )

    print(
        "Medication Reconciliation F1:",
        summary[
            "medication_reconciliation"
        ][
            "f1"
        ],
    )

    print()
    print(
        "SECONDARY METRICS"
    )

    print(
        "Medication Identity F1:",
        summary[
            "medication_identity"
        ][
            "f1"
        ],
    )

    print(
        "Dose Accuracy:",
        summary[
            "attributes"
        ][
            "dose"
        ][
            "accuracy"
        ],
    )

    print(
        "Frequency Accuracy:",
        summary[
            "attributes"
        ][
            "frequency"
        ][
            "accuracy"
        ],
    )

    print(
        "Route Accuracy:",
        summary[
            "attributes"
        ][
            "route"
        ][
            "accuracy"
        ],
    )

    print(
        "Status Accuracy:",
        summary[
            "attributes"
        ][
            "status"
        ][
            "accuracy"
        ],
    )

    print(
        "Discrepancy F1:",
        summary[
            "discrepancies"
        ][
            "f1"
        ],
    )

    print(
        "Interaction F1:",
        summary[
            "interactions"
        ][
            "f1"
        ],
    )

    print()
    print(
        "COMPARISON TARGETS"
    )

    print(
        "Frozen V0 Medication "
        f"Reconciliation F1: {V0_RECONCILIATION_F1:.4f}"
    )

    print(
        "Preserved V1 Medication "
        f"Reconciliation F1: {V1_RECONCILIATION_F1:.4f}"
    )

    print()

    v2_f1 = (
        summary[
            "medication_reconciliation"
        ][
            "f1"
        ]
    )

    v2_vs_v0 = (
        v2_f1
        - V0_RECONCILIATION_F1
    )

    v2_vs_v1 = (
        v2_f1
        - V1_RECONCILIATION_F1
    )

    print(
        "V2 absolute change vs V0:",
        round(
            v2_vs_v0,
            4,
        ),
    )

    print(
        "V2 absolute change vs V1:",
        round(
            v2_vs_v1,
            4,
        ),
    )

    print()

    if (
        v2_f1
        > V0_RECONCILIATION_F1
    ):
        print(
            "Result: V2 improved over V0."
        )

    elif (
        v2_f1
        == V0_RECONCILIATION_F1
    ):
        print(
            "Result: V2 matched V0."
        )

    else:
        print(
            "Result: V2 is currently below V0."
        )

    if (
        v2_f1
        > V1_RECONCILIATION_F1
    ):
        print(
            "Result: V2 improved over V1."
        )

    elif (
        v2_f1
        == V1_RECONCILIATION_F1
    ):
        print(
            "Result: V2 matched V1."
        )

    else:
        print(
            "Result: V2 is currently below V1."
        )

    print()
    print(
        "Evaluation artifact saved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()