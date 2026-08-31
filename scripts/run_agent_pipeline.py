"""
Run the MedRecon V1 agent pipeline across all synthetic evaluation cases.

Purpose:
    Produce reproducible agent-system predictions before evaluation.

Important:
    This script reads synthetic input cases only.

    It never loads ground-truth files.

Outputs:
    outputs/evaluations/agent_v1/SYN-XXX.json
    outputs/evaluations/agent_v1_results.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

BACKEND_DIR = (
    PROJECT_ROOT
    / "backend"
)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.services.orchestrator import (  # noqa: E402
    MedReconOrchestrator,
)


CASES_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "cases"
)

CASE_OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "agent_v1"
)

COMBINED_OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "agent_v1_results.json"
)


def load_json(
    path: Path,
) -> Any:
    """
    Load JSON data.
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
    Save formatted JSON.
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


def main() -> None:
    """
    Run V1 over every synthetic case.
    """
    case_files = sorted(
        CASES_DIR.glob(
            "SYN-*.json"
        )
    )

    if not case_files:
        raise FileNotFoundError(
            f"No synthetic cases found in "
            f"{CASES_DIR}"
        )

    orchestrator = (
        MedReconOrchestrator()
    )

    results: list[
        dict[str, Any]
    ] = []

    completed = 0
    failed = 0

    print(
        f"Running MedRecon V1 on "
        f"{len(case_files)} cases..."
    )

    for case_file in case_files:
        case = load_json(
            case_file
        )

        result = (
            orchestrator.run_case(
                case
            )
        )

        results.append(
            result
        )

        case_id = result[
            "case_id"
        ]

        save_json(
            CASE_OUTPUT_DIR
            / f"{case_id}.json",
            result,
        )

        if (
            result["status"]
            == "completed"
        ):
            completed += 1

            print(
                f"[OK] {case_id}"
            )

        else:
            failed += 1

            print(
                f"[FAILED] {case_id}: "
                f"{result.get('error')}"
            )

    combined = {
        "system": (
            "MedRecon AI"
        ),
        "version": "V1",
        "case_count": len(
            results
        ),
        "completed_count": (
            completed
        ),
        "failed_count": (
            failed
        ),
        "results": results,
    }

    save_json(
        COMBINED_OUTPUT_FILE,
        combined,
    )

    print()
    print(
        "Agent pipeline run complete."
    )

    print(
        "Completed:",
        completed,
    )

    print(
        "Failed:",
        failed,
    )

    print()
    print(
        "Combined output saved to:"
    )

    print(
        COMBINED_OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
