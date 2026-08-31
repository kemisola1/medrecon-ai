"""
FastAPI application entry point for MedRecon AI.

Purpose:
    Expose the MedRecon V3 medication reconciliation pipeline through HTTP.

Current endpoints:
    GET  /health
    POST /reconcile

Safety:
    MedRecon AI provides decision-support output only.

    It does not prescribe, discontinue, or change medication therapy.
    Consequential medication decisions require qualified human review.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.orchestrator import MedReconOrchestrator


app = FastAPI(
    title="MedRecon AI",
    version="3.0.0",
    description=(
        "Medication reconciliation and interaction-screening "
        "decision-support API."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


orchestrator = MedReconOrchestrator()


@app.get("/health")
def health() -> dict[str, str]:
    """
    Basic API health check.
    """
    return {
        "status": "ok",
        "system": "MedRecon AI",
        "pipeline_version": "V3",
    }


@app.post("/reconcile")
def reconcile_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """
    Run one medication reconciliation case through the V3 pipeline.

    Input:
        Synthetic or demo case containing:
            case_id
            sources

    Output:
        Reconciled medications
        discrepancies
        potential interaction findings
        agent trajectories
        execution metadata
    """
    return orchestrator.run_case(
        case
    )