"""
Generate synthetic medication-reconciliation evaluation cases.

Why this script exists:
    MedRecon AI needs a reproducible evaluation dataset that tests
    reconciliation behavior across clean, conflicting, temporal,
    ambiguous, and safety-related medication scenarios.

    Cases SYN-001 through SYN-006 are maintained manually as simple
    reference cases. This script generates SYN-007 through SYN-020.

Safety:
    All records generated here are synthetic. They do not represent
    real patients and must not be interpreted as clinical guidance.

Evaluation integrity:
    Input cases and expected ground truth are stored separately so
    MedRecon cannot use the expected answers while processing a case.
"""

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = PROJECT_ROOT / "data" / "synthetic" / "cases"
GROUND_TRUTH_DIR = PROJECT_ROOT / "data" / "synthetic" / "ground_truth"


def save_json(path: Path, data: dict[str, Any]) -> None:
    """
    Save structured synthetic data as readable JSON.

    Args:
        path:
            Destination file.

        data:
            JSON-serializable dictionary.

    Returns:
        None.

    Failure mode:
        File-system permission or serialization errors are allowed to
        surface so dataset generation never silently fails.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


CASES = [
    {
        "case_id": "SYN-007",
        "title": "Medication route changed",
        "description": (
            "A newer source explicitly changes the route of a medication."
        ),
        "sources": [
            {
                "source_id": "SRC-007-A",
                "type": "clinical_note",
                "name": "Previous Treatment Note",
                "date": "2026-08-08",
                "text": "Diclofenac 50 mg orally twice daily."
            },
            {
                "source_id": "SRC-007-B",
                "type": "clinical_note",
                "name": "Updated Treatment Note",
                "date": "2026-08-27",
                "text": (
                    "Stop oral Diclofenac. Start Diclofenac topical gel "
                    "applied twice daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-008",
        "title": "Conflicting medication status",
        "description": (
            "Two recent sources disagree about whether Losartan is current."
        ),
        "sources": [
            {
                "source_id": "SRC-008-A",
                "type": "prescription",
                "name": "Current Prescription",
                "date": "2026-08-25",
                "text": "Losartan 50 mg orally once daily."
            },
            {
                "source_id": "SRC-008-B",
                "type": "patient_report",
                "name": "Patient Medication Report",
                "date": "2026-08-26",
                "text": (
                    "Patient reports that Losartan was stopped and is "
                    "no longer being taken."
                )
            }
        ]
    },
    {
        "case_id": "SYN-009",
        "title": "Older source versus newer source",
        "description": (
            "A newer medication list should take temporal precedence "
            "over an older historical regimen."
        ),
        "sources": [
            {
                "source_id": "SRC-009-A",
                "type": "clinical_note",
                "name": "Old Clinic Note",
                "date": "2026-05-10",
                "text": "Atenolol 50 mg orally once daily."
            },
            {
                "source_id": "SRC-009-B",
                "type": "clinical_note",
                "name": "Current Clinic Note",
                "date": "2026-08-28",
                "text": (
                    "Atenolol was discontinued in June. Current medication "
                    "is Bisoprolol 5 mg orally once daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-010",
        "title": "Brand and generic medication names",
        "description": (
            "Different sources use brand and generic names for the same "
            "medication."
        ),
        "sources": [
            {
                "source_id": "SRC-010-A",
                "type": "prescription",
                "name": "Prescription",
                "date": "2026-08-20",
                "text": "Norvasc 5 mg orally once daily."
            },
            {
                "source_id": "SRC-010-B",
                "type": "clinical_note",
                "name": "Follow-up Note",
                "date": "2026-08-27",
                "text": "Continue Amlodipine 5 mg orally once daily."
            }
        ]
    },
    {
        "case_id": "SYN-011",
        "title": "Medication with missing dose",
        "description": (
            "A medication is documented as current but its dose is absent."
        ),
        "sources": [
            {
                "source_id": "SRC-011-A",
                "type": "patient_report",
                "name": "Patient Medication List",
                "date": "2026-08-27",
                "text": "Patient reports taking Metformin twice daily."
            }
        ]
    },
    {
        "case_id": "SYN-012",
        "title": "Medication with missing frequency",
        "description": (
            "A medication dose is documented but frequency is absent."
        ),
        "sources": [
            {
                "source_id": "SRC-012-A",
                "type": "clinical_note",
                "name": "Medication Review",
                "date": "2026-08-27",
                "text": "Current medication includes Amlodipine 5 mg orally."
            }
        ]
    },
    {
        "case_id": "SYN-013",
        "title": "Ambiguous medication identity",
        "description": (
            "A source contains an abbreviated medication name that should "
            "not be normalized by guessing."
        ),
        "sources": [
            {
                "source_id": "SRC-013-A",
                "type": "manual",
                "name": "Hand-entered Medication List",
                "date": "2026-08-27",
                "text": "Patient medication list includes 'MTX' once weekly."
            }
        ]
    },
    {
        "case_id": "SYN-014",
        "title": "Multiple conflicting documents",
        "description": (
            "Three sources contain inconsistent doses for the same medication."
        ),
        "sources": [
            {
                "source_id": "SRC-014-A",
                "type": "clinical_note",
                "name": "Clinic Note",
                "date": "2026-08-20",
                "text": "Gabapentin 100 mg orally three times daily."
            },
            {
                "source_id": "SRC-014-B",
                "type": "prescription",
                "name": "Prescription",
                "date": "2026-08-24",
                "text": "Gabapentin 300 mg orally three times daily."
            },
            {
                "source_id": "SRC-014-C",
                "type": "patient_report",
                "name": "Patient Report",
                "date": "2026-08-25",
                "text": (
                    "Patient reports taking Gabapentin 200 mg three "
                    "times daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-015",
        "title": "Potential medication interaction",
        "description": (
            "The reconciled medication set contains a synthetic "
            "interaction-screening scenario."
        ),
        "sources": [
            {
                "source_id": "SRC-015-A",
                "type": "prescription",
                "name": "Current Medication List",
                "date": "2026-08-28",
                "text": (
                    "Warfarin 5 mg orally once daily. "
                    "Trimethoprim-sulfamethoxazole 160/800 mg orally "
                    "twice daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-016",
        "title": "Historical medication mention",
        "description": (
            "A medication appears only as historical treatment and must "
            "not be classified as current."
        ),
        "sources": [
            {
                "source_id": "SRC-016-A",
                "type": "clinical_note",
                "name": "Current Consultation",
                "date": "2026-08-28",
                "text": (
                    "Patient previously used Simvastatin 20 mg nightly "
                    "but stopped it in 2025. Current medication is "
                    "Atorvastatin 20 mg orally once daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-017",
        "title": "Medication restarted",
        "description": (
            "A previously discontinued medication is explicitly restarted."
        ),
        "sources": [
            {
                "source_id": "SRC-017-A",
                "type": "clinical_note",
                "name": "Previous Visit",
                "date": "2026-07-15",
                "text": "Metformin 500 mg twice daily was discontinued."
            },
            {
                "source_id": "SRC-017-B",
                "type": "prescription",
                "name": "Current Prescription",
                "date": "2026-08-28",
                "text": (
                    "Restart Metformin 500 mg orally twice daily "
                    "effective today."
                )
            }
        ]
    },
    {
        "case_id": "SYN-018",
        "title": "Patient-reported medication discrepancy",
        "description": (
            "The prescription record and patient report disagree about "
            "the medication frequency."
        ),
        "sources": [
            {
                "source_id": "SRC-018-A",
                "type": "prescription",
                "name": "Prescription Record",
                "date": "2026-08-26",
                "text": "Furosemide 40 mg orally once daily."
            },
            {
                "source_id": "SRC-018-B",
                "type": "patient_report",
                "name": "Patient Interview",
                "date": "2026-08-28",
                "text": (
                    "Patient reports taking Furosemide 40 mg "
                    "twice daily."
                )
            }
        ]
    },
    {
        "case_id": "SYN-019",
        "title": "Adversarial irrelevant medication text",
        "description": (
            "The source contains medication-related language that does "
            "not describe the patient's medication regimen."
        ),
        "sources": [
            {
                "source_id": "SRC-019-A",
                "type": "clinical_note",
                "name": "Consultation Note",
                "date": "2026-08-28",
                "text": (
                    "Current medication: Amlodipine 5 mg orally once daily. "
                    "The patient asked whether a relative who takes Metformin "
                    "should attend a diabetes clinic. The clinician provided "
                    "general education about Aspirin but did not prescribe it "
                    "to this patient."
                )
            }
        ]
    },
    {
        "case_id": "SYN-020",
        "title": "Complex multi-medication reconciliation",
        "description": (
            "Multiple sources contain continued, changed, discontinued, "
            "new, and conflicting medication information."
        ),
        "sources": [
            {
                "source_id": "SRC-020-A",
                "type": "clinical_note",
                "name": "Previous Medication List",
                "date": "2026-08-10",
                "text": (
                    "Metformin 500 mg orally twice daily. "
                    "Amlodipine 5 mg orally once daily. "
                    "Lisinopril 10 mg orally once daily."
                )
            },
            {
                "source_id": "SRC-020-B",
                "type": "discharge_summary",
                "name": "Discharge Summary",
                "date": "2026-08-25",
                "text": (
                    "Continue Metformin 500 mg orally twice daily. "
                    "Increase Amlodipine to 10 mg orally once daily. "
                    "Discontinue Lisinopril. "
                    "Start Atorvastatin 20 mg orally once daily."
                )
            },
            {
                "source_id": "SRC-020-C",
                "type": "patient_report",
                "name": "Patient Interview",
                "date": "2026-08-28",
                "text": (
                    "Patient confirms Metformin 500 mg twice daily and "
                    "Atorvastatin 20 mg once daily, but reports still taking "
                    "Amlodipine 5 mg once daily."
                )
            }
        ]
    }
]


GROUND_TRUTH = [
    {
        "case_id": "SYN-007",
        "expected_medications": [
            {
                "medication_name": "Diclofenac",
                "dose": None,
                "frequency": "twice daily",
                "route": "topical",
                "status": "changed"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-008",
        "expected_medications": [
            {
                "medication_name": "Losartan",
                "dose": "50 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "conflicting"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Losartan",
                "type": "status_conflict",
                "severity": "medium"
            }
        ]
    },
    {
        "case_id": "SYN-009",
        "expected_medications": [
            {
                "medication_name": "Atenolol",
                "dose": "50 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "discontinued"
            },
            {
                "medication_name": "Bisoprolol",
                "dose": "5 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "recently_added"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-010",
        "expected_medications": [
            {
                "medication_name": "Amlodipine",
                "dose": "5 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "current"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-011",
        "expected_medications": [
            {
                "medication_name": "Metformin",
                "dose": None,
                "frequency": "twice daily",
                "route": None,
                "status": "uncertain"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Metformin",
                "type": "missing_information",
                "severity": "low"
            }
        ]
    },
    {
        "case_id": "SYN-012",
        "expected_medications": [
            {
                "medication_name": "Amlodipine",
                "dose": "5 mg",
                "frequency": None,
                "route": "oral",
                "status": "uncertain"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Amlodipine",
                "type": "missing_information",
                "severity": "low"
            }
        ]
    },
    {
        "case_id": "SYN-013",
        "expected_medications": [
            {
                "medication_name": "MTX",
                "dose": None,
                "frequency": "once weekly",
                "route": None,
                "status": "uncertain"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "MTX",
                "type": "missing_information",
                "severity": "medium"
            }
        ]
    },
    {
        "case_id": "SYN-014",
        "expected_medications": [
            {
                "medication_name": "Gabapentin",
                "dose": None,
                "frequency": "three times daily",
                "route": "oral",
                "status": "conflicting"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Gabapentin",
                "type": "dose_conflict",
                "severity": "medium"
            }
        ]
    },
    {
        "case_id": "SYN-015",
        "expected_medications": [
            {
                "medication_name": "Warfarin",
                "dose": "5 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "current"
            },
            {
                "medication_name": "Trimethoprim-sulfamethoxazole",
                "dose": "160/800 mg",
                "frequency": "twice daily",
                "route": "oral",
                "status": "current"
            }
        ],
        "expected_discrepancies": [],
        "expected_interactions": [
            {
                "medication_a": "Warfarin",
                "medication_b": "Trimethoprim-sulfamethoxazole",
                "severity": "high"
            }
        ]
    },
    {
        "case_id": "SYN-016",
        "expected_medications": [
            {
                "medication_name": "Simvastatin",
                "dose": "20 mg",
                "frequency": "nightly",
                "route": None,
                "status": "discontinued"
            },
            {
                "medication_name": "Atorvastatin",
                "dose": "20 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "current"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-017",
        "expected_medications": [
            {
                "medication_name": "Metformin",
                "dose": "500 mg",
                "frequency": "twice daily",
                "route": "oral",
                "status": "recently_added"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-018",
        "expected_medications": [
            {
                "medication_name": "Furosemide",
                "dose": "40 mg",
                "frequency": None,
                "route": "oral",
                "status": "conflicting"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Furosemide",
                "type": "frequency_conflict",
                "severity": "medium"
            }
        ]
    },
    {
        "case_id": "SYN-019",
        "expected_medications": [
            {
                "medication_name": "Amlodipine",
                "dose": "5 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "current"
            }
        ],
        "expected_discrepancies": []
    },
    {
        "case_id": "SYN-020",
        "expected_medications": [
            {
                "medication_name": "Metformin",
                "dose": "500 mg",
                "frequency": "twice daily",
                "route": "oral",
                "status": "current"
            },
            {
                "medication_name": "Amlodipine",
                "dose": None,
                "frequency": "once daily",
                "route": "oral",
                "status": "conflicting"
            },
            {
                "medication_name": "Lisinopril",
                "dose": "10 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "discontinued"
            },
            {
                "medication_name": "Atorvastatin",
                "dose": "20 mg",
                "frequency": "once daily",
                "route": "oral",
                "status": "recently_added"
            }
        ],
        "expected_discrepancies": [
            {
                "medication_name": "Amlodipine",
                "type": "dose_conflict",
                "severity": "medium"
            }
        ]
    }
]


def generate_cases() -> None:
    """
    Generate SYN-007 through SYN-020 and their ground truth.

    Existing files with the same identifiers are intentionally replaced
    so running this script always produces the same reproducible dataset.
    """
    for case in CASES:
        path = CASES_DIR / f"{case['case_id']}.json"
        save_json(path, case)

    for truth in GROUND_TRUTH:
        path = GROUND_TRUTH_DIR / f"{truth['case_id']}.json"
        save_json(path, truth)

    print(f"Generated {len(CASES)} synthetic cases.")
    print(f"Generated {len(GROUND_TRUTH)} ground-truth files.")
    print("SYN-007 through SYN-020 are ready.")


if __name__ == "__main__":
    generate_cases()