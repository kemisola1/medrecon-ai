"""
Validate the MedRecon AI synthetic evaluation dataset.

Why this script exists:
    Evaluation results are only meaningful when the underlying dataset
    is structurally consistent. This validator checks synthetic input
    cases and their separate ground-truth files before baseline or agent
    evaluation begins.

Safety:
    This validator performs structural checks only. It does not determine
    clinical correctness or provide medication advice.

Failure behavior:
    Validation errors are collected and displayed together so dataset
    problems can be corrected before evaluation.
"""

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CASES_DIR = PROJECT_ROOT / "data" / "synthetic" / "cases"
GROUND_TRUTH_DIR = (
    PROJECT_ROOT / "data" / "synthetic" / "ground_truth"
)

EXPECTED_CASE_IDS = {
    f"SYN-{number:03d}"
    for number in range(1, 21)
}

VALID_STATUSES = {
    "current",
    "recently_added",
    "discontinued",
    "changed",
    "conflicting",
    "uncertain",
}

VALID_DISCREPANCY_TYPES = {
    "dose_conflict",
    "frequency_conflict",
    "route_conflict",
    "status_conflict",
    "duplicate",
    "temporal_conflict",
    "missing_information",
}

VALID_SEVERITIES = {
    "high",
    "medium",
    "low",
}


def load_json(
    path: Path,
    errors: list[str],
) -> dict[str, Any] | None:
    """
    Load one JSON file safely.

    Args:
        path:
            JSON file to load.

        errors:
            Shared collection where validation failures are recorded.

    Returns:
        Parsed dictionary when successful, otherwise None.

    Failure modes:
        Missing files, invalid JSON, or non-object JSON are recorded
        rather than silently ignored.
    """
    if not path.exists():
        errors.append(f"Missing file: {path}")
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        errors.append(
            f"Invalid JSON in {path.name}: "
            f"line {exc.lineno}, column {exc.colno}"
        )
        return None

    if not isinstance(data, dict):
        errors.append(
            f"{path.name}: top-level JSON must be an object."
        )
        return None

    return data


def validate_case(
    case_id: str,
    data: dict[str, Any],
    errors: list[str],
) -> None:
    """
    Validate one synthetic input case.

    Checks:
        Case identity, descriptive fields, source structure, required
        source metadata, and duplicate source identifiers.
    """
    if data.get("case_id") != case_id:
        errors.append(
            f"{case_id}: case_id does not match filename."
        )

    if not data.get("title"):
        errors.append(f"{case_id}: missing title.")

    if not data.get("description"):
        errors.append(f"{case_id}: missing description.")

    sources = data.get("sources")

    if not isinstance(sources, list) or not sources:
        errors.append(
            f"{case_id}: sources must be a non-empty list."
        )
        return

    source_ids: set[str] = set()

    for index, source in enumerate(sources, start=1):
        label = f"{case_id} source #{index}"

        if not isinstance(source, dict):
            errors.append(f"{label}: source must be an object.")
            continue

        required_fields = {
            "source_id",
            "type",
            "name",
            "date",
            "text",
        }

        for field in required_fields:
            if not source.get(field):
                errors.append(
                    f"{label}: missing required field '{field}'."
                )

        source_id = source.get("source_id")

        if source_id:
            if source_id in source_ids:
                errors.append(
                    f"{case_id}: duplicate source_id '{source_id}'."
                )

            source_ids.add(source_id)


def validate_medication(
    case_id: str,
    medication: Any,
    index: int,
    errors: list[str],
) -> None:
    """
    Validate one expected reconciled medication record.
    """
    label = f"{case_id} expected medication #{index}"

    if not isinstance(medication, dict):
        errors.append(
            f"{label}: medication must be an object."
        )
        return

    if not medication.get("medication_name"):
        errors.append(
            f"{label}: missing medication_name."
        )

    status = medication.get("status")

    if status not in VALID_STATUSES:
        errors.append(
            f"{label}: unsupported status '{status}'."
        )

    for field in ("dose", "frequency", "route"):
        if field not in medication:
            errors.append(
                f"{label}: missing field '{field}'. "
                "Use null when intentionally unknown."
            )


def validate_discrepancy(
    case_id: str,
    discrepancy: Any,
    index: int,
    errors: list[str],
) -> None:
    """
    Validate one expected discrepancy.
    """
    label = f"{case_id} discrepancy #{index}"

    if not isinstance(discrepancy, dict):
        errors.append(
            f"{label}: discrepancy must be an object."
        )
        return

    if not discrepancy.get("medication_name"):
        errors.append(
            f"{label}: missing medication_name."
        )

    discrepancy_type = discrepancy.get("type")

    if discrepancy_type not in VALID_DISCREPANCY_TYPES:
        errors.append(
            f"{label}: unsupported type "
            f"'{discrepancy_type}'."
        )

    severity = discrepancy.get("severity")

    if severity not in VALID_SEVERITIES:
        errors.append(
            f"{label}: unsupported severity '{severity}'."
        )


def validate_interaction(
    case_id: str,
    interaction: Any,
    index: int,
    errors: list[str],
) -> None:
    """
    Validate one expected interaction record.

    This checks evaluation structure only. It does not independently
    verify whether the drug interaction is clinically correct.
    """
    label = f"{case_id} interaction #{index}"

    if not isinstance(interaction, dict):
        errors.append(
            f"{label}: interaction must be an object."
        )
        return

    for field in ("medication_a", "medication_b"):
        if not interaction.get(field):
            errors.append(
                f"{label}: missing '{field}'."
            )

    severity = interaction.get("severity")

    if severity not in VALID_SEVERITIES:
        errors.append(
            f"{label}: unsupported severity '{severity}'."
        )


def validate_ground_truth(
    case_id: str,
    data: dict[str, Any],
    errors: list[str],
) -> None:
    """
    Validate one ground-truth evaluation record.
    """
    if data.get("case_id") != case_id:
        errors.append(
            f"{case_id}: ground-truth case_id does not "
            "match filename."
        )

    medications = data.get("expected_medications")

    if not isinstance(medications, list):
        errors.append(
            f"{case_id}: expected_medications must be a list."
        )
    else:
        for index, medication in enumerate(
            medications,
            start=1,
        ):
            validate_medication(
                case_id,
                medication,
                index,
                errors,
            )

    discrepancies = data.get("expected_discrepancies")

    if not isinstance(discrepancies, list):
        errors.append(
            f"{case_id}: expected_discrepancies must be a list."
        )
    else:
        for index, discrepancy in enumerate(
            discrepancies,
            start=1,
        ):
            validate_discrepancy(
                case_id,
                discrepancy,
                index,
                errors,
            )

    interactions = data.get(
        "expected_interactions",
        [],
    )

    if not isinstance(interactions, list):
        errors.append(
            f"{case_id}: expected_interactions must be a list."
        )
    else:
        for index, interaction in enumerate(
            interactions,
            start=1,
        ):
            validate_interaction(
                case_id,
                interaction,
                index,
                errors,
            )


def validate_dataset() -> list[str]:
    """
    Validate the complete synthetic dataset.

    Returns:
        A list of validation errors. An empty list means the dataset
        passed all structural checks.
    """
    errors: list[str] = []

    case_files = {
        path.stem
        for path in CASES_DIR.glob("SYN-*.json")
    }

    truth_files = {
        path.stem
        for path in GROUND_TRUTH_DIR.glob("SYN-*.json")
    }

    missing_cases = EXPECTED_CASE_IDS - case_files
    missing_truth = EXPECTED_CASE_IDS - truth_files

    unexpected_cases = case_files - EXPECTED_CASE_IDS
    unexpected_truth = truth_files - EXPECTED_CASE_IDS

    for case_id in sorted(missing_cases):
        errors.append(
            f"Missing synthetic case: {case_id}"
        )

    for case_id in sorted(missing_truth):
        errors.append(
            f"Missing ground truth: {case_id}"
        )

    for case_id in sorted(unexpected_cases):
        errors.append(
            f"Unexpected synthetic case: {case_id}"
        )

    for case_id in sorted(unexpected_truth):
        errors.append(
            f"Unexpected ground truth: {case_id}"
        )

    for case_id in sorted(EXPECTED_CASE_IDS):
        case_path = CASES_DIR / f"{case_id}.json"
        truth_path = (
            GROUND_TRUTH_DIR / f"{case_id}.json"
        )

        case_data = load_json(case_path, errors)
        truth_data = load_json(truth_path, errors)

        if case_data is not None:
            validate_case(
                case_id,
                case_data,
                errors,
            )

        if truth_data is not None:
            validate_ground_truth(
                case_id,
                truth_data,
                errors,
            )

    return errors


def main() -> None:
    """
    Run dataset validation and print a human-readable report.
    """
    errors = validate_dataset()

    if errors:
        print(
            f"Dataset validation failed with "
            f"{len(errors)} error(s):"
        )

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    print("Dataset validation passed.")
    print("20 synthetic cases found.")
    print("20 matching ground-truth files found.")
    print("MedRecon evaluation dataset is ready.")


if __name__ == "__main__":
    main()