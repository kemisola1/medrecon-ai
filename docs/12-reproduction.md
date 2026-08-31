# MedRecon AI — Reproduction Guide

This guide explains how to reproduce the MedRecon AI baseline, agent iterations, final V3 system, and evaluation results from a clean environment.

## 1. Reference Environment

The project was developed and tested using:

```text
Operating System: Windows
Python: 3.12.6
Node.js: v20.18.0
npm: 10.9.0
```

Different compatible operating systems may also work, but the commands below reflect the reference Windows environment.

---

## 2. Clone the Repository

```bash
git clone https://github.com/kemisola1/medrecon-ai.git
cd medrecon-ai
```

---

## 3. Project Structure

Important project locations include:

```text
backend/
frontend/
data/
outputs/
scripts/
docs/
```

The project uses synthetic medication-reconciliation cases for hackathon evaluation.

No real patient data is required.

---

## 4. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the backend dependencies using the dependency file included in the repository.

For example:

```bash
pip install -r requirements.txt
```

Return to the repository root when running evaluation scripts:

```bash
cd ..
```

---

## 5. Verify the Backend

Start the FastAPI application:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Open:

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

Stop the server when necessary with:

```text
Ctrl + C
```

Return to the project root:

```bash
cd ..
```

---

# 6. Evaluation Dataset

MedRecon AI is evaluated on a fixed set of 20 synthetic medication-reconciliation cases.

The cases are designed to test situations including:

* medication identity
* dose changes
* frequency changes
* route changes
* discontinuation
* restarting medications
* recently added medications
* conflicting medication sources
* ambiguous medication identity
* irrelevant clinical text
* medication discrepancies
* medication interaction screening

The same evaluation dataset is used for the baseline and agent-based systems so that comparisons remain fair.

---

# 7. Primary Evaluation Metric

The primary metric is:

```text
Medication Reconciliation F1
```

A reconciled medication prediction is evaluated using medication attributes including:

* medication identity
* dose
* frequency
* route
* medication status

Secondary metrics include:

* Medication Identity F1
* Dose Accuracy
* Frequency Accuracy
* Route Accuracy
* Status Accuracy
* Discrepancy F1
* Interaction F1

---

# 8. V0 — Simple Baseline

V0 represents the simple pre-agent baseline.

From the repository root, run:

```bash
python scripts/run_baseline.py
```

Then evaluate the baseline:

```bash
python scripts/run_evaluation.py
```

Expected primary result:

```text
Medication Reconciliation F1: 0.6000
```

This result is treated as the frozen baseline for comparison with the agentic workflow.

---

# 9. V1 — First Agent Pipeline

Run the first agent-based implementation:

```bash
python scripts/run_agent_pipeline.py
```

Then run its evaluation:

```bash
python scripts/run_agent_evaluation.py
```

Expected primary result:

```text
Medication Reconciliation F1: 0.5902
```

V1 performed worse than the simple V0 baseline.

This experiment was not hidden or discarded from the evaluation history. It demonstrated that decomposing the task into agents did not automatically improve medication reconciliation.

The result informed the transition-aware and source-aware improvements made in V2.

---

# 10. V2 — Improved Reconciliation Pipeline

Run the V2 pipeline:

```bash
python scripts/run_agent_v2_pipeline.py
```

Then evaluate V2:

```bash
python scripts/run_agent_v2_evaluation.py
```

The V2 development process improved reconciliation through multiple refinements.

Recorded progression:

```text
Initial V2 reconciliation:       0.6885
Transition refinement:           0.7213
Final source-aware V2:           0.7541
```

The final V2 result substantially exceeded the V0 baseline.

---

# 11. V3 — Final Hackathon Pipeline

V3 preserves the improved reconciliation pipeline and adds medication interaction screening after medication reconciliation.

Run:

```bash
python scripts/run_agent_v3_pipeline.py
```

Expected execution summary:

```text
V3 agent pipeline run complete.
Completed: 20
Failed: 0
```

Then run the final evaluation:

```bash
python scripts/run_agent_v3_evaluation.py
```

Expected key results:

```text
Medication Reconciliation F1: 0.7541
Interaction F1: 1.0000
```

V3 preserves the final V2 reconciliation score while adding measurable medication interaction detection.

---

# 12. Final Baseline Comparison

The fixed evaluation benchmark produced the following progression:

| Version                  | Medication Reconciliation F1 |
| ------------------------ | ---------------------------: |
| V0 Baseline              |                       0.6000 |
| V1 Agent Pipeline        |                       0.5902 |
| V2 Initial               |                       0.6885 |
| V2 Transition Refinement |                       0.7213 |
| V2 Source-Aware Final    |                       0.7541 |
| V3 Final                 |                       0.7541 |

Final absolute improvement over V0:

```text
0.7541 - 0.6000 = +0.1541
```

V3 also achieved:

```text
Interaction F1: 1.0000
```

This interaction score applies only to the limited synthetic interaction benchmark used in this hackathon and should not be interpreted as clinical validation.

---

# 13. Final V3 Metrics

The final measured results include:

```text
Medication Reconciliation F1: 0.7541
Medication Identity F1:       0.9836
Dose Accuracy:                 0.9000
Frequency Accuracy:            0.8667
Route Accuracy:                1.0000
Status Accuracy:               0.8333
Discrepancy F1:                0.7273
Interaction F1:                1.0000
```

---

# 14. Evaluation Artifacts

Final V3 case-level outputs are stored under:

```text
outputs/evaluations/agent_v3/
```

The combined V3 results are stored at:

```text
outputs/evaluations/agent_v3_results.json
```

Final evaluation metrics are stored at:

```text
outputs/evaluations/agent_v3_metrics.json
```

These artifacts provide evidence for the reported benchmark results.

---

# 15. Medication Interaction Knowledge Source

The V3 interaction agent uses the deterministic medication interaction knowledge file:

```text
data/medications/interaction_knowledge.json
```

The Interaction Agent does not rely on unrestricted language-model memory to invent drug interaction facts.

For the hackathon implementation, only interactions represented in the approved synthetic knowledge base are evaluated.

Interaction findings are decision-support outputs and require qualified clinician or pharmacist review.

---

# 16. End-to-End Frontend Demo

The frontend is located in:

```text
frontend/
```

Install its dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

The backend must also be running.

In a separate terminal:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The frontend sends a medication-reconciliation request to:

```text
http://127.0.0.1:8000/reconcile
```

Click:

```text
Run MedRecon
```

The demo case contains:

```text
Warfarin 5 mg orally once daily

Trimethoprim-Sulfamethoxazole
160/800 mg orally twice daily
```

Expected output includes:

* a Reconciled Medication Picture
* medication discrepancies where applicable
* medication interaction findings
* a high-severity interaction warning
* evidence supporting the finding
* a qualified human-review requirement

This demonstrates the complete workflow from user interface to backend orchestration and final decision-support output.

---

# 17. Production Frontend Build

The frontend can be independently validated with:

```bash
cd frontend
npm run build
```

A successful build should finish without compilation failure and list the application routes.

---

# 18. Backend Tests

From the backend directory, run:

```bash
python -m pytest
```

During final submission validation, the project produced:

```text
2 passed
```

Warnings that do not fail the tests are not treated as successful functionality claims.

---

# 19. Agent Trajectories

Representative observable trajectories for every implemented agent are documented in:

```text
docs/11-agent-trajectories.md
```

Implemented agents are:

1. Intake & Extraction Agent
2. Medication Identity Agent
3. Medication Timeline Agent
4. Medication Reconciliation Agent
5. Medication Interaction Agent

The trajectories document observable inputs, outputs, tool interactions, evidence, failures, and human-review checkpoints.

Hidden chain-of-thought is not recorded or presented as an agent trajectory.

---

# 20. Human Review and Safety

MedRecon AI is a medication decision-support prototype.

It does not autonomously:

* prescribe medications
* discontinue medications
* modify medication orders
* diagnose patients
* execute treatment changes
* replace a clinician or pharmacist

The final output is described as a:

```text
Reconciled Medication Picture
```

rather than absolute clinical truth.

Potential medication-safety findings require qualified clinician or pharmacist review before consequential action.

All hackathon evaluation data are synthetic.

---

# 21. Approximate Runtime

Runtime depends on the computer used.

On a typical local development machine, the 20-case deterministic benchmark and evaluation scripts are designed to complete within a few minutes rather than requiring long-running model training.

The project does not require model training to reproduce the submitted benchmark.

---

# 22. Reproduction Cost

The submitted deterministic benchmark, reconciliation logic, interaction knowledge lookup, backend tests, and evaluation scripts can be reproduced locally without requiring paid external API calls.

Therefore, the expected external API cost for reproducing the submitted benchmark is:

```text
Approximately $0
```

This does not include the ordinary cost of the user's own computer, internet connection, or optional external services that are not required for the benchmark.

---

# 23. Clean Reproduction Sequence

A reviewer who wants to reproduce the main reported result can use this sequence from the repository root.

### Baseline

```bash
python scripts/run_baseline.py
python scripts/run_evaluation.py
```

Expected:

```text
Medication Reconciliation F1: 0.6000
```

### Final system

```bash
python scripts/run_agent_v3_pipeline.py
python scripts/run_agent_v3_evaluation.py
```

Expected:

```text
Completed: 20
Failed: 0
Medication Reconciliation F1: 0.7541
Interaction F1: 1.0000
```

The expected absolute reconciliation improvement is:

```text
+0.1541
```

---

# 24. Known Limitations

The hackathon prototype has important limitations:

* evaluation uses synthetic data
* the benchmark contains 20 cases
* medication interaction coverage is intentionally limited
* interaction performance has not been clinically validated
* the system is not connected to a production EHR
* the current UI is an MVP
* medication findings still require qualified human review

These limitations are deliberately disclosed rather than hidden.

---

# 25. Core Finding

The experiments showed that merely splitting medication reconciliation across several agents was not enough to improve performance.

The largest improvement came from better handling of medication transitions, source evidence, and current medication state.

This leads to the central MedRecon principle:

> Reconcile first. Alert second.

Medication safety screening becomes more meaningful only after the system has established which medications are actually current.
