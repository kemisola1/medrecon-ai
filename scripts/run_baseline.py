"""
Run the MedRecon AI V0 baseline across all synthetic evaluation cases.

Why this script exists:
    The hackathon requires the baseline and final agentic system to be
    evaluated on the same cases.

    This script creates reproducible baseline outputs that can later be
    compared against the synthetic ground truth.

Important:
    Ground-truth files are intentionally NOT loaded here.

    The baseline must generate its predictions independently. Ground truth
    will only be introduced later by the evaluation script.

Outputs:
    outputs/evaluations/baseline/SYN-001.json
    outputs/evaluations/baseline/SYN-002.json
    ...
    outputs/evaluations/baseline/SYN-020.json

    outputs/evaluations/baseline_results.json

Safety:
    This script operates only on synthetic hackathon cases.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BACKEND_DIR = PROJECT_ROOT / "backend"

CASES_DIR = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "cases"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "baseline"
)

COMBINED_OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "evaluations"
    / "baseline_results.json"
)


# The baseline service lives inside backend/app.
# Adding backend to sys.path allows this root-level script to import it
# without requiring the project to be installed as a Python package first.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.services.baseline_service import run_baseline


def load_json(
    path: Path,
) -> dict[str, Any]:
    """
    Load and parse one JSON file.

    Args:
        path:
            Path to the JSON file.

    Returns:
        Parsed JSON object.

    Raises:
        FileNotFoundError:
            If the requested file does not exist.

        json.JSONDecodeError:
            If the file contains invalid JSON.

    Why:
        Keeping file loading in one helper makes the baseline runner easier
        to read and gives us one place to manage JSON parsing behavior.
    """
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_json(
    path: Path,
    payload: Any,
) -> None:
    """
    Save a Python object as readable JSON.

    Args:
        path:
            Destination file path.

        payload:
            JSON-serializable object.

    Why:
        Evaluation artifacts should be human-readable so judges and
        developers can inspect the baseline outputs directly.
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


def discover_case_files() -> list[Path]:
    """
    Find all synthetic MedRecon evaluation case files.

    Returns:
        Sorted list of SYN-*.json files.

    Why:
        Sorting ensures the same deterministic case order every time
        the benchmark is executed.
    """
    return sorted(
        CASES_DIR.glob(
            "SYN-*.json"
        )
    )


def run_case(
    case_path: Path,
) -> dict[str, Any]:
    """
    Run the V0 baseline on one synthetic case.

    Args:
        case_path:
            Path to one synthetic case JSON file.

    Returns:
        Baseline result converted to a plain Python dictionary.

    Important:
        No ground-truth information is available to the baseline here.
    """
    case = load_json(
        case_path
    )

    result = run_baseline(
        case
    )

    return result.model_dump()


def run_all_cases() -> list[dict[str, Any]]:
    """
    Run the V0 baseline across every available synthetic case.

    Returns:
        List containing one baseline result per case.

    Side effects:
        Saves individual result files under:
            outputs/evaluations/baseline/

        Also saves:
            outputs/evaluations/baseline_results.json

    Failure behavior:
        A failing case is reported and re-raised rather than silently
        skipped. This prevents incomplete evaluation results from looking
        like a successful benchmark run.
    """
    case_files = discover_case_files()

    if not case_files:
        raise FileNotFoundError(
            "No synthetic cases were found in "
            f"{CASES_DIR}"
        )

    results: list[
        dict[str, Any]
    ] = []

    print(
        f"Found {len(case_files)} synthetic cases."
    )

    print(
        "Running MedRecon V0 baseline..."
    )

    for case_path in case_files:
        try:
            result = run_case(
                case_path
            )

        except Exception as exc:
            print(
                f"[FAILED] {case_path.name}: {exc}"
            )

            raise

        case_id = result[
            "case_id"
        ]

        output_path = (
            OUTPUT_DIR
            / f"{case_id}.json"
        )

        save_json(
            output_path,
            result,
        )

        results.append(
            result
        )

        medication_count = len(
            result.get(
                "medications",
                [],
            )
        )

        discrepancy_count = len(
            result.get(
                "discrepancies",
                [],
            )
        )

        interaction_count = len(
            result.get(
                "interactions",
                [],
            )
        )

        print(
            f"[OK] {case_id} | "
            f"medications={medication_count} | "
            f"discrepancies={discrepancy_count} | "
            f"interactions={interaction_count}"
        )

    combined_payload = {
        "baseline_version": "V0",
        "case_count": len(
            results
        ),
        "results": results,
    }

    save_json(
        COMBINED_OUTPUT_FILE,
        combined_payload,
    )

    return results


def main() -> None:
    """
    Command-line entry point for the baseline benchmark.

    Prints a concise completion summary after all cases have been processed.
    """
    results = run_all_cases()

    print()
    print(
        "Baseline run complete."
    )

    print(
        f"{len(results)} cases processed."
    )

    print(
        "Individual outputs:"
    )

    print(
        OUTPUT_DIR
    )

    print(
        "Combined output:"
    )

    print(
        COMBINED_OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
