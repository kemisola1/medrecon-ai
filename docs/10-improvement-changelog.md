# MedRecon AI — Improvement Changelog

## Purpose

This document records the measured development iterations of MedRecon AI.

Each major iteration documents:

- what was changed,
- why the change was attempted,
- the measured result,
- what was learned,
- and the decision that followed.

The same fixed 20-case synthetic evaluation set was used to compare the major system versions.

The primary metric is:

```text
Medication Reconciliation F1
```

---

# Experiment Summary

| Version | Reconciliation F1 | Interaction F1 | Outcome |
|---|---:|---:|---|
| V0 | 0.6000 | 0.0000 | Frozen baseline |
| V1 | 0.5902 | 0.0000 | Regression |
| V2 Initial | 0.6885 | 0.0000 | Improvement |
| V2 Transition Refinement | 0.7213 | 0.0000 | Improvement |
| V2 Source-Aware | 0.7541 | 0.0000 | Improvement |
| V3 | **0.7541** | **1.0000** | Reconciliation preserved + interaction screening added |

Final absolute reconciliation improvement over V0:

```text
+0.1541
```

---

# V0 — Frozen Deterministic Baseline

## Goal

Establish a simple and reproducible baseline before introducing the full agent workflow.

The purpose was not to create the strongest possible system, but to establish a fair reference point for later experiments.

## Result

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

## Observation

The baseline performed reasonably well on straightforward medication extraction and attribute matching.

Its largest weakness was medication-state reconstruction.

The status accuracy of:

```text
0.6897
```

showed that determining whether a medication was current, changed, discontinued, or otherwise unresolved was harder than simply recognizing the medication.

## Decision

Freeze V0.

All later versions would be compared against the same baseline rather than continually modifying the baseline.

---

# V1 — First Multi-Agent Pipeline

## What We Tried

V1 introduced the first specialized agent pipeline for medication reconstruction.

The workflow separated responsibilities across components rather than processing the entire medication history as one monolithic operation.

The pipeline introduced concepts including:

- intake and extraction,
- medication identity resolution,
- timeline construction,
- reconciliation,
- observable agent execution.

## Why

The hypothesis was that specialized agents would improve medication reconciliation by allowing each stage to focus on a narrower task.

## Result

```text
Medication Reconciliation F1: 0.5902
```

Compared with V0:

```text
V0 = 0.6000
V1 = 0.5902
```

Absolute change:

```text
-0.0098
```

## Outcome

V1 failed to outperform the baseline.

## What We Learned

This was an important failed experiment.

Agent decomposition alone did not improve the user outcome.

The pipeline could extract medication information, but reconciliation still struggled when the same medication appeared multiple times across a history.

Important failure modes included:

- repeated medication mentions,
- dose transitions,
- frequency transitions,
- discontinuation events,
- chronology,
- conflicting evidence.

The system needed to reason about medication **transitions**, not merely medication mentions.

## Decision

Keep the agent architecture, but redesign reconciliation around chronological medication events.

Do not hide or remove the V1 result.

It became the evidence motivating V2.

---

# V2 Iteration 1 — Transition-Aware Reconciliation

## What We Tried

V2 improved the Medication Reconciliation Agent's handling of sequential medication events.

Instead of treating repeated mentions as independent records, the system increasingly interpreted them as possible medication transitions.

Examples included:

```text
Amlodipine 5 mg
→
Amlodipine 10 mg
```

and:

```text
Metformin once daily
→
Metformin twice daily
```

## Why

V1 showed that the difficult part of medication reconciliation was often not identifying the medication.

The difficult part was determining what later evidence meant for earlier medication states.

## Result

```text
Medication Reconciliation F1: 0.6885
```

Improvement over V1:

```text
0.6885 - 0.5902 = +0.0983
```

Improvement over V0:

```text
0.6885 - 0.6000 = +0.0885
```

## What We Learned

Transition-aware reasoning produced a substantial improvement.

Chronology mattered.

However, several cases still required stronger confirmation before interpreting a later event as a definitive medication transition.

## Decision

Continue refining transition confirmation rather than adding additional agents.

---

# V2 Iteration 2 — Transition Confirmation Refinement

## What We Tried

The next iteration made medication transition handling more deliberate.

The system became more conservative about interpreting later medication events as definitive changes.

The goal was to distinguish between:

- genuine medication changes,
- repeated documentation,
- incomplete information,
- and conflicting evidence.

## Why

Over-aggressive transition interpretation could incorrectly overwrite valid earlier medication information.

The reconciliation agent needed stronger evidence before treating a medication attribute as definitively changed.

## Result

```text
Medication Reconciliation F1: 0.7213
```

Improvement from the previous V2 iteration:

```text
0.7213 - 0.6885 = +0.0328
```

Improvement over V0:

```text
0.7213 - 0.6000 = +0.1213
```

## What We Learned

More careful transition confirmation improved the primary metric again.

However, chronology alone was still insufficient for cases where different sources disagreed.

A patient report and an active prescription, for example, should not automatically be treated as equivalent evidence.

## Decision

Preserve source provenance through the pipeline and make reconciliation source-aware.

---

# V2 Iteration 3 — Source-Aware Reconciliation

## What We Tried

The next refinement preserved source provenance during intake and reconciliation.

A provenance issue was identified in which synthetic sources used:

```text
type
```

while part of the intake pipeline expected:

```text
source_type
```

The intake logic was corrected to preserve either representation.

Source-aware reconciliation could then distinguish evidence such as:

```text
prescription
```

from:

```text
patient_report
```

## Why

SYN-008 exposed an important medication-reconciliation problem.

An active structured medication source could conflict with a patient's report that they had stopped taking the medication.

The system should not silently choose one as truth.

It should represent the conflict.

## Result

```text
Medication Reconciliation F1: 0.7541
```

Improvement from the previous V2 iteration:

```text
0.7541 - 0.7213 = +0.0328
```

Improvement over V0:

```text
0.7541 - 0.6000 = +0.1541
```

## Representative Behavior

For conflicting evidence such as an active Losartan prescription and a patient report indicating the medication was stopped, MedRecon can produce:

```text
status: conflicting
needs_verification: true
```

and a discrepancy such as:

```text
status_conflict
```

The case is then surfaced for human review.

## What We Learned

Source provenance is part of medication meaning.

Medication reconciliation cannot reliably reason over fragmented evidence if the origin of that evidence is discarded during extraction.

## Decision

Freeze V2 reconciliation at:

```text
Medication Reconciliation F1 = 0.7541
```

Do not continue tuning the reconciliation rules solely to maximize the hackathon benchmark.

Move to the next product capability: medication interaction screening.

---

# V3 — Reconcile First, Alert Second

## What We Tried

V3 introduced the Medication Interaction Agent.

The key architectural decision was that the Interaction Agent would **not** screen every medication mention extracted from the raw sources.

Instead:

```text
Raw Medication Evidence
        ↓
Extraction
        ↓
Identity
        ↓
Timeline
        ↓
Reconciliation
        ↓
Interaction Screening
```

Only appropriate reconciled medication states are screened.

## Why

A medication appearing somewhere in a historical record does not necessarily mean the patient is currently taking it.

Running safety checks before reconciliation can therefore create irrelevant or misleading alerts.

The interaction system should consume the reconciled medication picture rather than the raw medication history.

## Implementation

The V3 Interaction Agent:

- receives reconciled medications,
- selects screenable medication states,
- normalizes medication names,
- creates order-independent medication pairs,
- checks those pairs against a deterministic knowledge base,
- records observable tool calls and results,
- preserves supporting medication evidence,
- creates human-review checkpoints.

Screenable statuses include:

```text
current
recently_added
changed
```

Interaction facts are not generated from unrestricted model memory.

---

# V3 Representative Interaction

The synthetic evaluation includes:

```text
Warfarin
+
Trimethoprim-Sulfamethoxazole
```

Both medications are first reconciled as current.

The interaction pair is then checked against the designated synthetic-approved knowledge base.

The resulting finding includes:

- drug A,
- drug B,
- interaction type,
- severity,
- summary,
- mechanism,
- recommended review action,
- verification status,
- knowledge source,
- medication evidence,
- human-review flag.

The finding contains:

```text
verification_status: knowledge_base_supported
needs_human_review: true
```

---

# V3 Result

Final evaluation:

```text
Medication Reconciliation F1: 0.7541
Medication Identity F1: 0.9836
Dose Accuracy: 0.9000
Frequency Accuracy: 0.8667
Route Accuracy: 1.0000
Status Accuracy: 0.8333
Discrepancy F1: 0.7273
Interaction F1: 1.0000
```

Comparison:

```text
V2 Reconciliation F1 = 0.7541
V3 Reconciliation F1 = 0.7541
```

Therefore:

```text
Reconciliation regression = 0.0000
```

V3 successfully added measurable interaction detection while preserving the frozen V2 reconciliation performance.

---

# Final Progression

The complete primary-metric progression was:

```text
V0
0.6000
   ↓
V1
0.5902
   ↓
V2 Initial
0.6885
   ↓
V2 Transition Refinement
0.7213
   ↓
V2 Source-Aware
0.7541
   ↓
V3
0.7541
```

The progression was not monotonic.

That is intentional to document.

The first agentic implementation made the system slightly worse before subsequent experiments identified the missing reasoning structure.

---

# Failed / Removed Experiment

The most important failed experiment was V1.

## Hypothesis

Breaking medication reconciliation into specialized agents would automatically outperform the deterministic baseline.

## Result

It did not.

```text
Baseline V0 = 0.6000
Agent V1    = 0.5902
```

## Why It Failed

The architecture had been decomposed into agents, but the difficult reconciliation logic had not yet been solved.

The system still needed stronger reasoning over:

- chronology,
- medication transitions,
- repeated mentions,
- source provenance,
- conflicting evidence.

## What We Did Next

We did **not** respond by adding more agents.

Instead, we improved the information available to the existing agents and refined the reconciliation rules.

This ultimately increased the score to:

```text
0.7541
```

## Lesson

> More agents do not automatically create a better agentic system.

Agent boundaries are useful only when they support the reasoning required by the user problem.

---

# Experiment We Deliberately Did Not Add

The architecture originally considered dedicated Verification and Prioritization Agents.

They were not added to the hackathon MVP.

## Why

The existing system already provides explicit:

```text
needs_verification
```

and:

```text
needs_human_review
```

boundaries.

Adding additional agents without enough time to evaluate their effect would have increased complexity without demonstrated user value.

The decision was therefore to preserve a smaller, measurable end-to-end workflow rather than add agents solely for architectural appearance.

Verification and prioritization remain future work.

---

# Key Product Insight

The experiments changed the project's view of where medication-safety intelligence begins.

The initial temptation was to focus on interaction detection.

The evaluation showed that the harder foundational problem was reconstructing the medication state correctly.

This produced the project's central insight:

> The most valuable agent in medication safety isn't the interaction checker; it's the agent that determines which medications are actually current before safety screening begins.

Or more simply:

> **Reconcile first. Alert second.**

---

# Final Outcome

Compared with the frozen baseline:

```text
V0 Medication Reconciliation F1 = 0.6000
V3 Medication Reconciliation F1 = 0.7541
```

Absolute improvement:

```text
+0.1541
```

V3 also added:

```text
Interaction F1 = 1.0000
```

on the fixed synthetic benchmark without reducing reconciliation performance.

The most important result of the experiment was therefore not the number of agents.

It was the evolution from a medication-list processor into a source-aware, timeline-aware reconciliation workflow that performs safety screening only after reconstructing the medication picture.