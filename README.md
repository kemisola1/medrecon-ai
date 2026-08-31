# MedRecon AI

> Reconcile. Understand. Verify.

**MedRecon** AI is an agentic medication intelligence platform that reconstructs a patient's medication history from fragmented healthcare information, identifies the best-supported current medication picture, detects discrepancies and potential medication-safety concerns, and provides evidence-backed findings for qualified human review.

**Core principle:** Reconcile first. Alert second.

**Primary users**: nurses, pharmacists, physicians, clinicians, and medication-reconciliation teams who need to review fragmented medication histories and establish the best-supported current medication picture before medication-safety decisions are made.

---

## The Problem

Medication information is often fragmented across prescriptions, clinical notes, discharge summaries, pharmacy records, patient reports, and electronic health records.

Before medication-safety screening can be useful, a healthcare professional first needs to answer a more fundamental question:

> Which medications is this patient actually taking now?

A medication may have been discontinued, restarted, increased, decreased, replaced, reported differently by the patient, or documented inconsistently across multiple sources.

Running interaction checks directly against an unreconciled medication list can therefore produce misleading or clinically irrelevant alerts.

MedRecon AI addresses this by reconstructing the medication picture **before** performing safety screening.

---

## What MedRecon Does

MedRecon processes fragmented medication information through a sequence of specialized agents:

```text
Medication Sources
       ↓
Intake & Extraction Agent
       ↓
Medication Identity Agent
       ↓
Medication Timeline Agent
       ↓
Medication Reconciliation Agent
       ↓
Interaction Screening Agent
       ↓
Human Review
```

The resulting **Reconciled Medication Picture** can contain:

- current medications
- recently added medications
- discontinued medications
- medication changes
- uncertain medication states
- conflicting medication information
- medication discrepancies
- potential drug-drug interactions
- supporting source evidence
- verification flags
- human-review checkpoints

---

## Agentic Architecture

MedRecon uses specialized agents rather than one monolithic medication-processing step.

### 1. Intake & Extraction Agent

Extracts medication mentions and medication attributes from fragmented source text.

It identifies information such as:

- medication name
- dose
- frequency
- route
- medication status
- source
- source date
- evidence text

Repeated medication mentions are preserved rather than collapsed prematurely.

### 2. Medication Identity Agent

Normalizes medication identities across different representations.

For example:

```text
Norvasc → Amlodipine
```

Ambiguous identities are not silently resolved. They can instead be marked for verification.

### 3. Medication Timeline Agent

Orders medication events chronologically and groups events belonging to the same medication.

This allows MedRecon to reason over medication transitions rather than treating every source as an independent medication list.

### 4. Medication Reconciliation Agent

Constructs the best-supported medication picture from the available evidence.

It handles scenarios including:

- dose changes
- frequency changes
- route changes
- discontinuations
- additions
- conflicting sources
- missing medication attributes

Unresolved or conflicting information is explicitly surfaced for human review.

### 5. Medication Interaction Agent

Screens reconciled medications against a designated deterministic interaction knowledge base.

Interaction screening occurs **after reconciliation**.

The agent does not invent interaction facts from model memory.

Potential findings include:

- interacting medication pair
- severity
- interaction summary
- mechanism
- recommended review action
- knowledge source
- medication evidence
- human-review requirement

---

## Why Reconciliation Comes First

A conventional workflow might do:

```text
Medication list
      ↓
Interaction checker
```

MedRecon instead performs:

```text
Fragmented medication evidence
      ↓
Identity resolution
      ↓
Timeline reconstruction
      ↓
Medication reconciliation
      ↓
Interaction screening
```

This design reflects the project's central hypothesis:

> Medication-safety screening becomes more useful when the system first determines which medications are actually supported as current.

---

## End-to-End Demo

The repository includes a working web interface connected to the FastAPI backend.

The demo submits medication information through the frontend and runs it through the V3 agent pipeline.

A representative demo includes:

```text
Warfarin 5 mg orally once daily

Trimethoprim-Sulfamethoxazole
160/800 mg orally twice daily
```

MedRecon:

1. extracts both medication events,
2. resolves their medication identities,
3. reconstructs their timeline,
4. reconciles them as active medications,
5. screens the reconciled medication picture,
6. identifies the knowledge-supported interaction,
7. returns the source evidence, and
8. flags the finding for qualified clinician or pharmacist review.

The interface displays:

- Reconciled Medication Picture
- medication status
- discrepancies
- potential interaction findings
- severity
- recommended review action
- human-review warnings

---

## Evaluation

MedRecon was evaluated on **20 synthetic medication-reconciliation cases**.

The same evaluation cases and comparison rules were preserved across system versions.

### Primary Metric

**Medication Reconciliation F1**

A medication counts as a strict reconciliation match only when all of the following match synthetic ground truth:

- medication identity
- dose
- frequency
- route
- status

### Final V3 Results

| Metric | Result |
|---|---:|
| Medication Reconciliation F1 | **0.7541** |
| Medication Identity F1 | **0.9836** |
| Dose Accuracy | **0.9000** |
| Frequency Accuracy | **0.8667** |
| Route Accuracy | **1.0000** |
| Status Accuracy | **0.8333** |
| Discrepancy F1 | **0.7273** |
| Interaction F1 | **1.0000** |

---

## Measured Improvement

Development preserved unsuccessful experiments rather than hiding them.

| Version | Medication Reconciliation F1 | Key Change |
|---|---:|---|
| V0 | 0.6000 | Frozen deterministic baseline |
| V1 | 0.5902 | First multi-agent reconciliation pipeline |
| V2 | 0.7541 | Improved transition and source-aware reconciliation |
| V3 | 0.7541 | Added deterministic interaction screening |

V3 absolute improvement over V0:

```text
+0.1541
```

V3 absolute improvement over V1:

```text
+0.1639
```

V3 preserved V2 reconciliation performance while adding:

```text
Interaction F1 = 1.0000
```

### What the Failed V1 Experiment Taught Us

The first agentic implementation did **not** automatically outperform the simpler baseline.

```text
V0: 0.6000
V1: 0.5902
```

This was retained as a legitimate failed experiment.

Analysis showed that introducing multiple agents was insufficient by itself. The system needed better handling of:

- repeated medication mentions
- explicit medication transitions
- chronological evidence
- source provenance
- patient-reported conflicts

Those findings informed V2.

---

## Evaluation Cases

The synthetic evaluation suite contains 20 cases covering scenarios such as:

- clean medication lists
- dose conflicts
- medication discontinuation
- newly added medications
- dose increases
- frequency changes
- route changes
- patient-report conflicts
- medication replacement
- brand/generic normalization
- missing dose
- missing frequency
- ambiguous medication identity
- multiple dose transitions
- drug-drug interaction screening
- medication switching
- medication restart
- frequency conflict
- irrelevant source text
- complex conflicting medication histories

Synthetic data is used to avoid exposing real patient information.

---

## Observable Agent Trajectories

MedRecon stores observable execution traces for agent runs.

Trajectory events include:

- input received
- validation
- decisions
- tool calls
- tool results
- output creation
- retries where applicable
- human checkpoints
- errors

The trajectories contain operationally useful execution information without storing hidden chain-of-thought.

Representative trajectories are documented in:

```text
docs/11-agent-trajectories.md
```

---

## Human Review

MedRecon is designed as a **decision-support system**, not an autonomous clinical decision-maker.

Human-review checkpoints are created when findings require professional judgment.

Examples include:

- unresolved medication identity
- conflicting medication status
- uncertain medication information
- potential medication interactions

Potential interactions are explicitly marked:

```text
needs_human_review: true
```

Consequential medication decisions remain the responsibility of qualified healthcare professionals.

---

## Safety Boundaries

MedRecon AI does **not**:

- prescribe medication
- discontinue medication
- modify medication orders
- recommend autonomous dose changes
- diagnose patients
- replace pharmacists
- replace clinicians
- execute consequential clinical actions

Interaction findings are generated from a designated knowledge source rather than unrestricted model memory.

The current knowledge base is intentionally synthetic and limited for hackathon evaluation.

The MVP uses synthetic patient cases only.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- custom agent orchestration
- deterministic medication interaction knowledge base

### Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS

### Evaluation

- synthetic medication cases
- synthetic ground truth
- deterministic evaluation scripts
- versioned evaluation artifacts

---

## Repository Structure

```text
medrecon-ai/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│       └── app/
│
├── data/
│   ├── synthetic/
│   │   ├── cases/
│   │   └── ground_truth/
│   └── medications/
│       └── interaction_knowledge.json
│
├── docs/
│   ├── 01-product-specification.md
│   ├── 02-architecture.md
│   ├── 03-data-model.md
│   ├── 04-agent-specifications.md
│   ├── 05-api.md
│   ├── 06-ui.md
│   ├── 07-safety.md
│   ├── 08-evaluation.md
│   ├── 09-baseline.md
│   ├── 10-improvement-changelog.md
│   ├── 11-agent-trajectories.md
│   ├── 12-reproduction.md
│   └── 13-demo-script.md
│
├── outputs/
│   └── evaluations/
│
├── scripts/
│   ├── run_agent_pipeline.py
│   ├── run_agent_evaluation.py
│   ├── run_agent_v2_pipeline.py
│   ├── run_agent_v2_evaluation.py
│   ├── run_agent_v3_pipeline.py
│   └── run_agent_v3_evaluation.py
│
└── README.md
```

---

# Running MedRecon Locally

## 1. Clone the Repository

```bash
git clone https://github.com/kemisola1/medrecon-ai.git
cd medrecon-ai
```

## 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create and activate a Python virtual environment if desired.

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
GET /health
```

Medication reconciliation endpoint:

```text
POST /reconcile
```

---

## 3. Frontend Setup

Open another terminal from the repository root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The web interface runs locally at:

```text
http://localhost:3000
```

Keep both the frontend and backend running for the end-to-end demo.

---

# Reproducing the Evaluation

From the repository root, run the V3 pipeline:

```bash
python scripts/run_agent_v3_pipeline.py
```

Expected:

```text
Running MedRecon V3 on 20 cases...

...

V3 agent pipeline run complete.
Completed: 20
Failed: 0
```

Then evaluate the predictions:

```bash
python scripts/run_agent_v3_evaluation.py
```

Expected final metrics include:

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

Evaluation artifact:

```text
outputs/evaluations/agent_v3_metrics.json
```

Detailed reproduction instructions are available in:

```text
docs/12-reproduction.md
```

---

## Experiment History

The repository intentionally preserves previous system versions.

### V0

Frozen deterministic baseline.

```text
Medication Reconciliation F1 = 0.6000
```

### V1

First agent pipeline.

```text
Medication Reconciliation F1 = 0.5902
```

V1 was preserved as a failed experiment.

### V2

Improved reconciliation logic.

```text
Medication Reconciliation F1 = 0.7541
```

### V3

Added deterministic interaction screening after reconciliation.

```text
Medication Reconciliation F1 = 0.7541
Interaction F1 = 1.0000
```

See:

```text
docs/10-improvement-changelog.md
```

for the complete experiment history.

---

## Hackathon Hot Take

> **The most valuable agent in medication safety isn't the interaction checker; it's the agent that determines which medications are actually current before safety screening begins.**

Medication interaction systems are only as useful as the medication list they receive.

MedRecon therefore treats medication reconciliation as a prerequisite for downstream medication-safety intelligence.

---

## Current Limitations

This is a hackathon MVP.

Current limitations include:

- synthetic evaluation data
- limited deterministic interaction knowledge base
- rule-based extraction and reconciliation components
- limited medication vocabulary
- no production EHR/FHIR integration
- no production authentication or authorization
- no autonomous clinical verification
- no real-patient validation
- no deployment for clinical use

These limitations are intentional and should be addressed before any real-world clinical application.

---

## Future Work

Potential extensions include:

- FHIR/EHR integration
- prescription and discharge-summary ingestion
- PDF and document extraction
- expanded medication terminology
- validated drug knowledge APIs
- dedicated verification agent
- prioritization agent
- clinician feedback loops
- calibrated confidence scoring
- audit dashboards
- prospective clinical validation

---

## Documentation

Detailed project documentation is available in the `docs/` directory.

Key files:

```text
docs/02-architecture.md
docs/04-agent-specifications.md
docs/07-safety.md
docs/08-evaluation.md
docs/09-baseline.md
docs/10-improvement-changelog.md
docs/11-agent-trajectories.md
docs/12-reproduction.md
docs/13-demo-script.md
```

---

## Disclaimer

MedRecon AI is a hackathon research prototype using synthetic data.

It is not a medical device and is not intended for clinical use, diagnosis, prescribing, medication modification, or autonomous medical decision-making.

All medication-safety findings require review by an appropriately qualified healthcare professional.# MedRecon AI

> Reconcile. Understand. Verify.

**MedRecon AI** is an agentic medication intelligence platform that reconstructs a patient's medication history from fragmented healthcare information, identifies the best-supported current medication picture, detects discrepancies and potential medication-safety concerns, and provides evidence-backed findings for qualified human review.

**Core principle:** Reconcile first. Alert second.

---

## The Problem

Medication information is often fragmented across prescriptions, clinical notes, discharge summaries, pharmacy records, patient reports, and electronic health records.

Before medication-safety screening can be useful, a healthcare professional first needs to answer a more fundamental question:

> Which medications is this patient actually taking now?

A medication may have been discontinued, restarted, increased, decreased, replaced, reported differently by the patient, or documented inconsistently across multiple sources.

Running interaction checks directly against an unreconciled medication list can therefore produce misleading or clinically irrelevant alerts.

MedRecon AI addresses this by reconstructing the medication picture **before** performing safety screening.

---

## What MedRecon Does

MedRecon processes fragmented medication information through a sequence of specialized agents:

```text
Medication Sources
       ↓
Intake & Extraction Agent
       ↓
Medication Identity Agent
       ↓
Medication Timeline Agent
       ↓
Medication Reconciliation Agent
       ↓
Interaction Screening Agent
       ↓
Human Review
```

The resulting **Reconciled Medication Picture** can contain:

- current medications
- recently added medications
- discontinued medications
- medication changes
- uncertain medication states
- conflicting medication information
- medication discrepancies
- potential drug-drug interactions
- supporting source evidence
- verification flags
- human-review checkpoints

---

## Agentic Architecture

MedRecon uses specialized agents rather than one monolithic medication-processing step.

### 1. Intake & Extraction Agent

Extracts medication mentions and medication attributes from fragmented source text.

It identifies information such as:

- medication name
- dose
- frequency
- route
- medication status
- source
- source date
- evidence text

Repeated medication mentions are preserved rather than collapsed prematurely.

### 2. Medication Identity Agent

Normalizes medication identities across different representations.

For example:

```text
Norvasc → Amlodipine
```

Ambiguous identities are not silently resolved. They can instead be marked for verification.

### 3. Medication Timeline Agent

Orders medication events chronologically and groups events belonging to the same medication.

This allows MedRecon to reason over medication transitions rather than treating every source as an independent medication list.

### 4. Medication Reconciliation Agent

Constructs the best-supported medication picture from the available evidence.

It handles scenarios including:

- dose changes
- frequency changes
- route changes
- discontinuations
- additions
- conflicting sources
- missing medication attributes

Unresolved or conflicting information is explicitly surfaced for human review.

### 5. Medication Interaction Agent

Screens reconciled medications against a designated deterministic interaction knowledge base.

Interaction screening occurs **after reconciliation**.

The agent does not invent interaction facts from model memory.

Potential findings include:

- interacting medication pair
- severity
- interaction summary
- mechanism
- recommended review action
- knowledge source
- medication evidence
- human-review requirement

---

## Why Reconciliation Comes First

A conventional workflow might do:

```text
Medication list
      ↓
Interaction checker
```

MedRecon instead performs:

```text
Fragmented medication evidence
      ↓
Identity resolution
      ↓
Timeline reconstruction
      ↓
Medication reconciliation
      ↓
Interaction screening
```

This design reflects the project's central hypothesis:

> Medication-safety screening becomes more useful when the system first determines which medications are actually supported as current.

---

## End-to-End Demo

The repository includes a working web interface connected to the FastAPI backend.

The demo submits medication information through the frontend and runs it through the V3 agent pipeline.

A representative demo includes:

```text
Warfarin 5 mg orally once daily

Trimethoprim-Sulfamethoxazole
160/800 mg orally twice daily
```

MedRecon:

1. extracts both medication events,
2. resolves their medication identities,
3. reconstructs their timeline,
4. reconciles them as active medications,
5. screens the reconciled medication picture,
6. identifies the knowledge-supported interaction,
7. returns the source evidence, and
8. flags the finding for qualified clinician or pharmacist review.

The interface displays:

- Reconciled Medication Picture
- medication status
- discrepancies
- potential interaction findings
- severity
- recommended review action
- human-review warnings

---

## Evaluation

MedRecon was evaluated on **20 synthetic medication-reconciliation cases**.

The same evaluation cases and comparison rules were preserved across system versions.

### Primary Metric

**Medication Reconciliation F1**

A medication counts as a strict reconciliation match only when all of the following match synthetic ground truth:

- medication identity
- dose
- frequency
- route
- status

### Final V3 Results

| Metric | Result |
|---|---:|
| Medication Reconciliation F1 | **0.7541** |
| Medication Identity F1 | **0.9836** |
| Dose Accuracy | **0.9000** |
| Frequency Accuracy | **0.8667** |
| Route Accuracy | **1.0000** |
| Status Accuracy | **0.8333** |
| Discrepancy F1 | **0.7273** |
| Interaction F1 | **1.0000** |

---

## Measured Improvement

Development preserved unsuccessful experiments rather than hiding them.

| Version | Medication Reconciliation F1 | Key Change |
|---|---:|---|
| V0 | 0.6000 | Frozen deterministic baseline |
| V1 | 0.5902 | First multi-agent reconciliation pipeline |
| V2 | 0.7541 | Improved transition and source-aware reconciliation |
| V3 | 0.7541 | Added deterministic interaction screening |

V3 absolute improvement over V0:

```text
+0.1541
```

V3 absolute improvement over V1:

```text
+0.1639
```

V3 preserved V2 reconciliation performance while adding:

```text
Interaction F1 = 1.0000
```

### What the Failed V1 Experiment Taught Us

The first agentic implementation did **not** automatically outperform the simpler baseline.

```text
V0: 0.6000
V1: 0.5902
```

This was retained as a legitimate failed experiment.

Analysis showed that introducing multiple agents was insufficient by itself. The system needed better handling of:

- repeated medication mentions
- explicit medication transitions
- chronological evidence
- source provenance
- patient-reported conflicts

Those findings informed V2.

---

## Evaluation Cases

The synthetic evaluation suite contains 20 cases covering scenarios such as:

- clean medication lists
- dose conflicts
- medication discontinuation
- newly added medications
- dose increases
- frequency changes
- route changes
- patient-report conflicts
- medication replacement
- brand/generic normalization
- missing dose
- missing frequency
- ambiguous medication identity
- multiple dose transitions
- drug-drug interaction screening
- medication switching
- medication restart
- frequency conflict
- irrelevant source text
- complex conflicting medication histories

Synthetic data is used to avoid exposing real patient information.

---

## Observable Agent Trajectories

MedRecon stores observable execution traces for agent runs.

Trajectory events include:

- input received
- validation
- decisions
- tool calls
- tool results
- output creation
- retries where applicable
- human checkpoints
- errors

The trajectories contain operationally useful execution information without storing hidden chain-of-thought.

Representative trajectories are documented in:

```text
docs/11-agent-trajectories.md
```

---

## Human Review

MedRecon is designed as a **decision-support system**, not an autonomous clinical decision-maker.

Human-review checkpoints are created when findings require professional judgment.

Examples include:

- unresolved medication identity
- conflicting medication status
- uncertain medication information
- potential medication interactions

Potential interactions are explicitly marked:

```text
needs_human_review: true
```

Consequential medication decisions remain the responsibility of qualified healthcare professionals.

---

## Safety Boundaries

MedRecon AI does **not**:

- prescribe medication
- discontinue medication
- modify medication orders
- recommend autonomous dose changes
- diagnose patients
- replace pharmacists
- replace clinicians
- execute consequential clinical actions

Interaction findings are generated from a designated knowledge source rather than unrestricted model memory.

The current knowledge base is intentionally synthetic and limited for hackathon evaluation.

The MVP uses synthetic patient cases only.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- custom agent orchestration
- deterministic medication interaction knowledge base

### Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS

### Evaluation

- synthetic medication cases
- synthetic ground truth
- deterministic evaluation scripts
- versioned evaluation artifacts

---

## Repository Structure

```text
medrecon-ai/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   └── src/
│       └── app/
│
├── data/
│   ├── synthetic/
│   │   ├── cases/
│   │   └── ground_truth/
│   └── medications/
│       └── interaction_knowledge.json
│
├── docs/
│   ├── 01-product-specification.md
│   ├── 02-architecture.md
│   ├── 03-data-model.md
│   ├── 04-agent-specifications.md
│   ├── 05-api.md
│   ├── 06-ui.md
│   ├── 07-safety.md
│   ├── 08-evaluation.md
│   ├── 09-baseline.md
│   ├── 10-improvement-changelog.md
│   ├── 11-agent-trajectories.md
│   ├── 12-reproduction.md
│   └── 13-demo-script.md
│
├── outputs/
│   └── evaluations/
│
├── scripts/
│   ├── run_agent_pipeline.py
│   ├── run_agent_evaluation.py
│   ├── run_agent_v2_pipeline.py
│   ├── run_agent_v2_evaluation.py
│   ├── run_agent_v3_pipeline.py
│   └── run_agent_v3_evaluation.py
│
└── README.md
```

---

# Running MedRecon Locally

## 1. Clone the Repository

```bash
git clone https://github.com/kemisola1/medrecon-ai.git
cd medrecon-ai
```

## 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create and activate a Python virtual environment if desired.

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest
```

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
GET /health
```

Medication reconciliation endpoint:

```text
POST /reconcile
```

---

## 3. Frontend Setup

Open another terminal from the repository root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The web interface runs locally at:

```text
http://localhost:3000
```

Keep both the frontend and backend running for the end-to-end demo.

---

# Reproducing the Evaluation

From the repository root, run the V3 pipeline:

```bash
python scripts/run_agent_v3_pipeline.py
```

Expected:

```text
Running MedRecon V3 on 20 cases...

...

V3 agent pipeline run complete.
Completed: 20
Failed: 0
```

Then evaluate the predictions:

```bash
python scripts/run_agent_v3_evaluation.py
```

Expected final metrics include:

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

Evaluation artifact:

```text
outputs/evaluations/agent_v3_metrics.json
```

Detailed reproduction instructions are available in:

```text
docs/12-reproduction.md
```

---

## Experiment History

The repository intentionally preserves previous system versions.

### V0

Frozen deterministic baseline.

```text
Medication Reconciliation F1 = 0.6000
```

### V1

First agent pipeline.

```text
Medication Reconciliation F1 = 0.5902
```

V1 was preserved as a failed experiment.

### V2

Improved reconciliation logic.

```text
Medication Reconciliation F1 = 0.7541
```

### V3

Added deterministic interaction screening after reconciliation.

```text
Medication Reconciliation F1 = 0.7541
Interaction F1 = 1.0000
```

See:

```text
docs/10-improvement-changelog.md
```

for the complete experiment history.

---

## Hackathon Hot Take

> **The most valuable agent in medication safety isn't the interaction checker; it's the agent that determines which medications are actually current before safety screening begins.**

Medication interaction systems are only as useful as the medication list they receive.

MedRecon therefore treats medication reconciliation as a prerequisite for downstream medication-safety intelligence.

---

## Current Limitations

This is a hackathon MVP.

Current limitations include:

- synthetic evaluation data
- limited deterministic interaction knowledge base
- rule-based extraction and reconciliation components
- limited medication vocabulary
- no production EHR/FHIR integration
- no production authentication or authorization
- no autonomous clinical verification
- no real-patient validation
- no deployment for clinical use

These limitations are intentional and should be addressed before any real-world clinical application.

---

## Future Work

Potential extensions include:

- FHIR/EHR integration
- prescription and discharge-summary ingestion
- PDF and document extraction
- expanded medication terminology
- validated drug knowledge APIs
- dedicated verification agent
- prioritization agent
- clinician feedback loops
- calibrated confidence scoring
- audit dashboards
- prospective clinical validation

---

## Documentation

Detailed project documentation is available in the `docs/` directory.

Key files:

```text
docs/02-architecture.md
docs/04-agent-specifications.md
docs/07-safety.md
docs/08-evaluation.md
docs/09-baseline.md
docs/10-improvement-changelog.md
docs/11-agent-trajectories.md
docs/12-reproduction.md
docs/13-demo-script.md
```

---

## Disclaimer

MedRecon AI is a hackathon research prototype using synthetic data.

It is not a medical device and is not intended for clinical use, diagnosis, prescribing, medication modification, or autonomous medical decision-making.

All medication-safety findings require review by an appropriately qualified healthcare professional.
