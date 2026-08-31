# MedRecon AI — Representative Agent Trajectories

## 1. Purpose

MedRecon AI records observable execution trajectories so that agent behavior can be inspected, evaluated, and reproduced.

These trajectories document operational events such as:

- agent input
- validation
- medication evidence processed
- tool calls
- tool results
- generated outputs
- verification flags
- human-review checkpoints
- execution errors where applicable

They do not attempt to expose or store hidden chain-of-thought.

The implemented V3 pipeline contains five agents:

```text
1. Intake & Extraction Agent
2. Medication Identity Agent
3. Medication Timeline Agent
4. Medication Reconciliation Agent
5. Medication Interaction Agent
```

The representative examples below use the synthetic evaluation workflow, particularly SYN-015, which demonstrates the complete V3 path from medication evidence to interaction screening.

---

# 2. End-to-End V3 Trajectory

The overall execution sequence is:

```text
Synthetic Case
      ↓
IntakeExtractionAgent
      ↓
MedicationIdentityAgent
      ↓
MedicationTimelineAgent
      ↓
MedicationReconciliationAgent
      ↓
MedicationInteractionAgent
      ↓
Evidence-Backed Findings
      ↓
Human Review
```

Each agent receives structured output from the preceding stage.

This makes the intermediate state observable and allows failures to be localized to a specific stage.

---

# 3. Agent 1 — Intake & Extraction Agent

## Responsibility

The Intake & Extraction Agent converts fragmented source information into structured medication events.

It preserves source provenance so downstream agents can reason about where medication information came from.

Representative inputs may include:

```text
prescription
patient_report
clinical_note
discharge_summary
pharmacy_record
```

For the synthetic hackathon dataset, sources contain structured metadata and medication-related text.

---

## Representative Input — SYN-015

Example source:

```text
Source type: prescription
Source date: 2026-08-28

Warfarin
Trimethoprim-Sulfamethoxazole
```

---

## Observable Processing

The agent inspects the source and extracts medication-event attributes such as:

```text
medication_name
dose
frequency
route
status
source_type
source_date
evidence
```

Source provenance is retained.

The intake layer supports source metadata represented as either:

```text
source_type
```

or:

```text
type
```

This became important during the source-aware V2 reconciliation experiment.

---

## Representative Output

Conceptually:

```json
{
  "medication_name": "Warfarin",
  "status": "current",
  "source_type": "prescription",
  "source_date": "2026-08-28"
}
```

and:

```json
{
  "medication_name": "Trimethoprim-Sulfamethoxazole",
  "status": "current",
  "source_type": "prescription",
  "source_date": "2026-08-28"
}
```

---

## Validation / Retry Behavior

If medication information is incomplete, the agent does not invent missing clinical facts.

Missing or uncertain fields remain unresolved for later reconciliation or human verification.

Execution failures are represented as observable errors rather than silently discarded.

---

## Human Checkpoint

Extraction alone does not authorize any medication decision.

Uncertain medication information can propagate as:

```text
needs_verification: true
```

for downstream review.

---

# 4. Agent 2 — Medication Identity Agent

## Responsibility

The Medication Identity Agent determines whether medication mentions refer to the same normalized medication identity.

This is important because healthcare records may use:

- brand names
- generic names
- abbreviations
- inconsistent capitalization
- alternative text representations

---

## Representative Normalization

A synthetic example is:

```text
Norvasc
   ↓
Amlodipine
```

The normalized identity allows downstream agents to reason over the medication history as one medication rather than two unrelated entries.

---

## Representative Input

Conceptually:

```json
{
  "medication_name": "Norvasc"
}
```

---

## Representative Output

```json
{
  "medication_name": "Amlodipine"
}
```

For SYN-015:

```text
Warfarin
→ Warfarin

Trimethoprim-Sulfamethoxazole
→ Trimethoprim-Sulfamethoxazole
```

No unnecessary identity transformation is applied.

---

## Ambiguity Handling

The agent does not silently force an identity when the available evidence is insufficient.

An ambiguous medication identity can remain uncertain and be marked for verification.

A representative synthetic challenge is an abbreviated medication such as:

```text
MTX
```

where the system should avoid unsupported certainty.

---

## Human Checkpoint

Ambiguous identity resolution can result in:

```text
needs_verification: true
```

This prevents uncertain medication identity from being treated as confirmed clinical truth.

---

# 5. Agent 3 — Medication Timeline Agent

## Responsibility

The Medication Timeline Agent organizes medication events chronologically.

Its purpose is to convert disconnected medication mentions into a sequence that the reconciliation agent can interpret.

---

## Why Timeline Reconstruction Matters

Consider:

```text
Amlodipine 5 mg
```

followed later by:

```text
Amlodipine 10 mg
```

Without chronology, these could appear to be two contradictory medication records.

With timeline information, the reconciliation agent can evaluate whether the later evidence represents a dose transition.

---

## Representative Input

Conceptually:

```text
Medication: Amlodipine
Earlier event: 5 mg
Later event: 10 mg
```

---

## Representative Output

```text
Amlodipine
│
├── earlier event: 5 mg
│
└── later event: 10 mg
```

The agent groups events belonging to the same normalized medication and orders them using available dates.

---

## SYN-015 Behavior

For SYN-015, both medications are supported by the prescription dated:

```text
2026-08-28
```

The timeline therefore preserves both as relevant medication events for reconciliation.

---

## Validation Behavior

The timeline agent does not independently prescribe meaning to every sequence.

Chronological ordering provides evidence to the Reconciliation Agent.

For example:

```text
earlier dose
+
later dose
```

does not automatically mean:

```text
confirmed dose change
```

The Reconciliation Agent determines whether the available evidence supports that interpretation.

---

# 6. Agent 4 — Medication Reconciliation Agent

## Responsibility

The Medication Reconciliation Agent constructs the best-supported medication picture from the available medication events.

This is the core reasoning stage of MedRecon AI.

---

## Inputs

The agent receives:

- normalized medication identities
- chronological medication events
- medication attributes
- source provenance
- supporting evidence

---

## Possible Reconciled States

The agent can produce medication states such as:

```text
current
recently_added
changed
discontinued
conflicting
uncertain
```

---

## Representative Transition

Input:

```text
Amlodipine 5 mg
        ↓
Amlodipine 10 mg
```

Possible reconciled interpretation:

```text
Amlodipine 10 mg
status: changed
```

when the evidence supports a confirmed transition.

---

## Representative Conflict — SYN-008

SYN-008 contains conflicting medication evidence involving Losartan.

One source supports an active medication state while patient-reported evidence indicates that the medication was stopped.

Rather than silently selecting one source as absolute truth, the source-aware reconciliation logic can produce:

```text
Losartan
status: conflicting
needs_verification: true
```

and a discrepancy:

```text
status_conflict
```

---

## Human Checkpoint

A conflicting medication state requires human verification.

The agent therefore preserves the uncertainty instead of autonomously deciding whether the patient should continue or stop the medication.

---

## Representative SYN-015 Output

For SYN-015, reconciliation produces:

```text
Trimethoprim-Sulfamethoxazole — current
Warfarin — current
```

These reconciled states become the input to interaction screening.

This ordering is important.

The Interaction Agent does not receive every historical medication mention indiscriminately.

---

# 7. Agent 5 — Medication Interaction Agent

## Responsibility

The Medication Interaction Agent screens the reconciled medication picture for supported medication interactions.

It runs **after reconciliation**.

---

## Screenable Medication States

The current V3 implementation screens medications with states including:

```text
current
recently_added
changed
```

Historical or otherwise non-screenable medication states are not automatically treated as active interaction candidates.

---

## Representative Input — SYN-015

```text
Trimethoprim-Sulfamethoxazole — current
Warfarin — current
```

---

## Tool Call

The agent normalizes medication names and creates an order-independent medication-pair key.

It then queries the designated deterministic interaction knowledge base.

Conceptually:

```text
TOOL_CALL

Lookup interaction:

Trimethoprim-Sulfamethoxazole
+
Warfarin
```

---

## Tool Result

The designated knowledge source contains a supported interaction for the pair.

Conceptually:

```text
TOOL_RESULT

match: true
severity: high
type: drug_drug_interaction
verification_status: knowledge_base_supported
```

---

## Finding

The agent returns an evidence-backed interaction finding containing:

```text
drug_a
drug_b
type
severity
summary
mechanism
recommended_action
verification_status
knowledge_source
medication_evidence
needs_human_review
```

Representative safety fields:

```text
severity: high
verification_status: knowledge_base_supported
needs_human_review: true
```

---

## Knowledge Boundary

The interaction agent does not use unrestricted model memory as the authoritative source of interaction facts.

The current hackathon implementation uses:

```text
data/medications/interaction_knowledge.json
```

as its deterministic synthetic-approved knowledge source.

This makes the interaction lookup reproducible and auditable.

---

## Human Checkpoint

After a supported interaction is identified, the agent creates a human-review checkpoint.

The system does not autonomously:

```text
stop Warfarin
stop Trimethoprim-Sulfamethoxazole
change either dose
replace either medication
issue a prescription
```

Instead, the finding recommends review by an appropriately qualified clinician or pharmacist.

---

# 8. Representative Full SYN-015 Flow

The complete observable flow can be summarized as:

```text
INPUT
│
│ Prescription evidence
│ Warfarin
│ Trimethoprim-Sulfamethoxazole
│
▼
INTAKE & EXTRACTION
│
│ Medication events extracted
│ Provenance preserved
│
▼
MEDICATION IDENTITY
│
│ Warfarin normalized
│ TMP-SMX identity normalized
│
▼
TIMELINE
│
│ Events ordered using source evidence
│
▼
RECONCILIATION
│
│ Warfarin → current
│ Trimethoprim-Sulfamethoxazole → current
│
▼
INTERACTION TOOL CALL
│
│ Check normalized medication pair
│
▼
INTERACTION TOOL RESULT
│
│ Knowledge-base match
│ Severity: high
│
▼
INTERACTION FINDING
│
│ verification_status:
│ knowledge_base_supported
│
│ needs_human_review:
│ true
│
▼
HUMAN REVIEW
```

This trajectory demonstrates the project's core principle:

> Reconcile first. Alert second.

---

# 9. Failed-Trajectory Learning — V1

Observable trajectories were also useful for understanding the failed V1 experiment.

V1 produced:

```text
Medication Reconciliation F1 = 0.5902
```

compared with:

```text
V0 = 0.6000
```

The failure showed that successfully passing information between multiple agents did not guarantee correct reconciliation.

The problem was not simply agent execution.

The problem was the quality of the medication state represented between those stages.

Subsequent iterations improved:

- medication transitions
- chronological interpretation
- source provenance
- conflicting evidence handling

This eventually produced:

```text
V2/V3 Medication Reconciliation F1 = 0.7541
```

---

# 10. Human Review Checkpoints

Human checkpoints are an explicit part of the architecture.

They are used when the system encounters consequential uncertainty or medication-safety findings.

Examples include:

### Uncertain Identity

```text
needs_verification: true
```

### Conflicting Medication Status

```text
status: conflicting
needs_verification: true
```

### Potential Interaction

```text
needs_human_review: true
```

The checkpoint is a safety boundary.

It is not an instruction for the system to autonomously resolve the clinical question.

---

# 11. What Is Not Stored

MedRecon trajectories are intended to capture observable system execution.

They do not depend on storing hidden chain-of-thought.

Useful audit information includes:

```text
agent
input
structured output
tool call
tool result
validation result
error
human checkpoint
```

This is sufficient to inspect how information moved through the medication workflow without requiring private reasoning traces.

---

# 12. Reproducibility

V3 trajectories can be generated by running:

```bash
python scripts/run_agent_v3_pipeline.py
```

The pipeline processes the fixed synthetic evaluation cases and produces versioned outputs under:

```text
outputs/evaluations/agent_v3/
```

The combined output is stored at:

```text
outputs/evaluations/agent_v3_results.json
```

These artifacts can be inspected to observe the outputs produced by the complete V3 pipeline.

---

# 13. Implemented vs Future Agents

The hackathon MVP implements:

```text
✓ Intake & Extraction Agent
✓ Medication Identity Agent
✓ Medication Timeline Agent
✓ Medication Reconciliation Agent
✓ Medication Interaction Agent
```

Dedicated agents for the following are not currently implemented:

```text
Verification Agent
Prioritization Agent
```

Verification and prioritization remain future extensions.

The current MVP instead uses explicit verification flags and human-review checkpoints to preserve the clinical safety boundary.

---

## Conclusion

MedRecon's agent trajectories demonstrate an end-to-end workflow in which each specialized agent contributes to a specific part of medication reconstruction.

The most important architectural dependency is:

```text
Interaction Screening
        depends on
Medication Reconciliation
```

The SYN-015 trajectory demonstrates this directly:

```text
fragmented evidence
→ structured medication events
→ normalized identities
→ medication timeline
→ reconciled current medications
→ deterministic interaction lookup
→ evidence-backed finding
→ qualified human review
```

This makes the workflow inspectable, reproducible, and aligned with MedRecon's central design principle:

> **Reconcile first. Alert second.**