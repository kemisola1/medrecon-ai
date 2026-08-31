# MedRecon AI — Reproduction Guide

## 1. Purpose

This guide explains how to reproduce the MedRecon AI hackathon MVP from a clean environment.

It covers:

- backend setup
- frontend setup
- baseline execution
- V1 evaluation
- V2 evaluation
- V3 evaluation
- end-to-end demo execution
- output locations
- expected metrics
- environment versions

The project uses synthetic medication data only.

---

# 2. Reference Environment

The project was developed and tested using:

```text
Python 3.12.6
Node.js v20.18.0
npm 10.9.0
```

Operating system used during development:

```text
Windows
```

The repository is available at:

```text
https://github.com/kemisola1/medrecon-ai
```

---

# 3. Clone the Repository

Run:

```bash
git clone https://github.com/kemisola1/medrecon-ai.git
cd medrecon-ai
```

Repository structure:

```text
medrecon-ai/
├── backend/
├── frontend/
├── data/
├── docs/
├── outputs/
├── scripts/
└── README.md
```

---

# 4. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Optional but recommended: create a virtual environment.

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend test suite:

```bash
python -m pytest
```

Start the FastAPI development server:

```bash
python -m uvicorn app.main:app --reload
```

Expected local API address:

```text
http://127.0.0.1:8000
```

---

# 5. Verify the Backend

With the server running, open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "system": "MedRecon AI",
  "pipeline_version": "V3"
}
```

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Frontend Setup

Open a second terminal from the repository root.

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

Expected local frontend address:

```text
http://localhost:3000
```

Keep both servers running:

```text
Frontend:
http://localhost:3000

Backend:
http://127.0.0.1:8000
```

---

# 7. End-to-End Demo

Open:

```text
http://localhost:3000
```

The MedRecon AI demo page contains a synthetic medication case.

Click:

```text
Run MedRecon
```

The frontend sends the case to:

```text
POST /reconcile
```

The backend then executes the V3 agent pipeline.

The demo medication pair includes:

```text
Warfarin
Trimethoprim-Sulfamethoxazole
```

Expected visible output includes:

```text
Reconciled Medication Picture
```

with both medications represented as active/current medications.

The interface should also display a:

```text
high-severity potential interaction
```

and a human-review warning.

Representative safety output includes:

```text
needs_human_review: true
```

---

# 8. Evaluation Dataset

The project uses a fixed synthetic benchmark of:

```text
20 cases
```

The cases cover:

- clean medication lists
- dose conflicts
- discontinuation
- recently added medication
- dose transitions
- frequency transitions
- route transitions
- patient-reported conflicts
- medication replacement
- brand/generic normalization
- missing medication attributes
- ambiguous medication identity
- multiple dose events
- interaction screening
- medication switching
- medication restart
- frequency conflict
- irrelevant text
- complex medication histories

The same benchmark is used for comparison between major versions.

---

# 9. Primary Evaluation Metric

The main metric is:

```text
Medication Reconciliation F1
```

A strict medication match requires agreement on:

```text
medication identity
dose
frequency
route
status
```

Additional metrics include:

```text
Medication Identity F1
Dose Accuracy
Frequency Accuracy
Route Accuracy
Status Accuracy
Discrepancy F1
Interaction F1
```

---

# 10. Running the Frozen V0 Baseline

From the repository root, run the existing baseline pipeline and evaluation scripts included in the repository.

Use the V0 scripts defined under:

```text
scripts/
```

The frozen baseline result is:

```text
Medication Reconciliation F1: 0.6000
Medication Identity F1: 0.9667
Dose Accuracy: 0.8621
Frequency Accuracy: 1.0000
Route Accuracy: 0.9655
Status Accuracy: 0.6897
Discrepancy F1: 0.8000
Interaction F1: 0.0000
```

The V0 baseline is intentionally frozen.

It should not be modified when reproducing comparisons with later versions.

---

# 11. Running V1

From the repository root, run:

```bash
python scripts/run_agent_pipeline.py
```

Then evaluate:

```bash
python scripts/run_agent_evaluation.py
```

The primary V1 result is:

```text
Medication Reconciliation F1: 0.5902
```

This result is intentionally retained even though it performs slightly worse than the frozen V0 baseline.

Comparison:

```text
V0: 0.6000
V1: 0.5902
```

This failed experiment motivated the transition-aware V2 design.

---

# 12. Running V2

From the repository root, run:

```bash
python scripts/run_agent_v2_pipeline.py
```

Then evaluate:

```bash
python scripts/run_agent_v2_evaluation.py
```

Final frozen V2 metrics:

```text
Medication Reconciliation F1: 0.7541
Medication Identity F1: 0.9836
Dose Accuracy: 0.9000
Frequency Accuracy: 0.8667
Route Accuracy: 1.0000
Status Accuracy: 0.8333
Discrepancy F1: 0.7273
Interaction F1: 0.0000
```

The final V2 primary result is:

```text
Medication Reconciliation F1 = 0.7541
```

---

# 13. Running V3

V3 adds interaction screening after reconciliation.

From the repository root, run:

```bash
python scripts/run_agent_v3_pipeline.py
```

Expected pipeline summary:

```text
V3 agent pipeline run complete.
Completed: 20
Failed: 0
```

Then run:

```bash
python scripts/run_agent_v3_evaluation.py
```

Expected final metrics:

```text
Medication Reconciliation F1: 0.7541
Medication Identity F1: 0.9836
Dose Accuracy: 0.9
Frequency Accuracy: 0.8667
Route Accuracy: 1.0
Status Accuracy: 0.8333
Discrepancy F1: 0.7273
Interaction F1: 1.0
```

---

# 14. Version Comparison

Expected comparison:

```text
V0 Medication Reconciliation F1: 0.6000
V1 Medication Reconciliation F1: 0.5902
V2 Medication Reconciliation F1: 0.7541
V3 Medication Reconciliation F1: 0.7541
```

Final V3 improvement over V0:

```text
0.7541 - 0.6000 = +0.1541
```

Final V3 improvement over V1:

```text
0.7541 - 0.5902 = +0.1639
```

V3 change relative to V2:

```text
0.7541 - 0.7541 = 0.0000
```

This means V3 added interaction screening without reducing the final reconciliation score.

---

# 15. V2 Iteration History

The V2 development process included multiple measured iterations.

Results:

```text
V2 Initial:
0.6885

V2 Transition Refinement:
0.7213

V2 Source-Aware:
0.7541
```

These results are preserved in the experiment documentation.

See:

```text
docs/10-improvement-changelog.md
```

---

# 16. V3 Interaction Test

The representative interaction case is:

```text
SYN-015
```

The reconciled medications include:

```text
Trimethoprim-Sulfamethoxazole — current
Warfarin — current
```

The interaction agent then checks the pair against:

```text
data/medications/interaction_knowledge.json
```

Expected interaction output contains fields including:

```text
type: drug_drug_interaction
severity: high
verification_status: knowledge_base_supported
needs_human_review: true
```

The expected interaction metric is:

```text
Interaction F1 = 1.0000
```

This value represents performance only on the current synthetic benchmark and limited hackathon knowledge base.

It is not a claim of comprehensive clinical drug-interaction coverage.

---

# 17. Output Locations

## V3 Per-Case Outputs

```text
outputs/evaluations/agent_v3/
```

Examples:

```text
outputs/evaluations/agent_v3/SYN-001.json
outputs/evaluations/agent_v3/SYN-015.json
```

## Combined V3 Output

```text
outputs/evaluations/agent_v3_results.json
```

## Final V3 Metrics

```text
outputs/evaluations/agent_v3_metrics.json
```

Previous evaluation outputs are preserved for comparison where applicable.

---

# 18. Interaction Knowledge Base

The V3 interaction system uses:

```text
data/medications/interaction_knowledge.json
```

The knowledge base is deterministic and intentionally limited for hackathon evaluation.

The interaction agent does not rely on unrestricted model memory as the authoritative source for interaction facts.

This allows the same interaction test to produce reproducible results.

---

# 19. Agent Execution Order

The V3 pipeline executes:

```text
IntakeExtractionAgent
        ↓
MedicationIdentityAgent
        ↓
MedicationTimelineAgent
        ↓
MedicationReconciliationAgent
        ↓
MedicationInteractionAgent
```

The interaction agent receives reconciled medication information rather than raw medication mentions.

This is intentional.

The core architecture is:

```text
Reconcile first.
Alert second.
```

---

# 20. Safety Reproduction

The representative interaction finding should include:

```text
needs_human_review: true
```

The system does not autonomously:

```text
prescribe
discontinue
modify medication
change dose
replace medication
make treatment decisions
```

A qualified healthcare professional remains responsible for consequential medication decisions.

---

# 21. Reproducing Agent Trajectories

Run:

```bash
python scripts/run_agent_v3_pipeline.py
```

Then inspect the generated V3 case outputs and combined output.

Representative trajectory documentation is also available at:

```text
docs/11-agent-trajectories.md
```

The observable trajectory may include:

```text
agent execution
structured input
structured output
tool calls
tool results
human checkpoints
errors
```

The system does not require disclosure of hidden chain-of-thought.

---

# 22. Frontend Production Check

From:

```text
frontend/
```

run:

```bash
npm run build
```

A successful build provides an additional verification that the frontend compiles correctly for production.

The hackathon demo itself can still be run with:

```bash
npm run dev
```

---

# 23. Backend Test Check

From:

```text
backend/
```

run:

```bash
python -m pytest
```

The tests should complete without failures before final submission.

---

# 24. Clean Reproduction Sequence

A clean reproduction can therefore be summarized as:

```bash
git clone https://github.com/kemisola1/medrecon-ai.git

cd medrecon-ai

cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
python -m uvicorn app.main:app --reload
```

Open a second terminal:

```bash
cd medrecon-ai\frontend
npm install
npm run dev
```

Open a third terminal from the repository root:

```bash
cd medrecon-ai

python scripts/run_agent_v3_pipeline.py
python scripts/run_agent_v3_evaluation.py
```

Open:

```text
http://localhost:3000
```

and click:

```text
Run MedRecon
```

---

# 25. Expected Final Evidence

A successful reproduction should demonstrate:

```text
20 V3 cases completed
0 V3 pipeline failures
Medication Reconciliation F1 = 0.7541
Interaction F1 = 1.0000
Frontend renders successfully
Frontend can call the FastAPI backend
Warfarin is reconciled
Trimethoprim-Sulfamethoxazole is reconciled
High-severity interaction finding appears
Human-review warning appears
```

---

# 26. Runtime and Cost Notes

The hackathon evaluation pipeline is designed to be reproducible locally.

The current interaction lookup is deterministic and uses a local JSON knowledge base.

No external production drug database is required to reproduce the submitted V3 interaction result.

The current benchmark uses only 20 synthetic cases and is therefore intended as a hackathon-scale evaluation rather than a production workload benchmark.

No claim is made that the current runtime, infrastructure, or knowledge-base coverage is suitable for clinical production use.

---

# 27. Known Limitations

The reproduction environment demonstrates a research prototype.

Important limitations include:

```text
synthetic data only
small evaluation dataset
limited medication vocabulary
limited interaction knowledge base
no real-patient validation
no production EHR integration
no production authentication
no autonomous clinical verification
```

These limitations should be preserved when interpreting the reported results.

---

# 28. Supporting Documentation

For additional detail:

```text
docs/08-evaluation.md
docs/09-baseline.md
docs/10-improvement-changelog.md
docs/11-agent-trajectories.md
docs/13-demo-script.md
```

---

## Final Reproduction Target

The central reproducible result of the submission is:

```text
Frozen V0 Reconciliation F1 = 0.6000

Final V3 Reconciliation F1 = 0.7541

Final V3 Interaction F1 = 1.0000
```

combined with a working end-to-end interface demonstrating:

```text
source medication evidence
→ extraction
→ identity
→ timeline
→ reconciliation
→ interaction screening
→ human review
```

This reproduces the core MedRecon AI principle:

> **Reconcile first. Alert second.**
