# MedRecon AI — Evaluation

## 1. Evaluation Objective

The evaluation measures whether MedRecon AI can reconstruct an accurate medication picture from fragmented medication information while identifying clinically relevant discrepancies and medication-safety signals.

The evaluation was designed around the project's central hypothesis:

> Medication-safety screening should occur after the medication history has been reconciled.

The primary evaluation therefore focuses on medication reconciliation quality, with additional metrics for medication identity, attributes, discrepancies, and interaction detection.

---

## 2. Evaluation Dataset

MedRecon AI is evaluated using a fixed synthetic dataset containing:

```text
20 medication reconciliation cases
```

Synthetic data was used to avoid exposing real patient information and to provide explicit ground truth for deterministic evaluation.

The same evaluation cases are used across the baseline and subsequent agent versions so that performance comparisons remain consistent.

Cases include both straightforward and challenging medication-history scenarios.

### Covered Scenarios

The evaluation set includes:

1. clean medication lists
2. dose conflicts
3. medication discontinuation
4. newly added medications
5. dose increases
6. frequency changes
7. route changes
8. patient-reported status conflicts
9. medication replacement
10. brand/generic normalization
11. missing dose information
12. missing frequency information
13. ambiguous medication identity
14. multiple dose transitions
15. drug-drug interaction screening
16. medication switching
17. medication restart
18. frequency conflicts
19. irrelevant source text
20. complex conflicting medication histories

These cases test whether the system can reason over medication events rather than simply extract medication names.

---

# 3. Primary Metric

The primary metric is:

```text
Medication Reconciliation F1
```

This metric was selected because producing the correct reconciled medication picture is the central user outcome of MedRecon AI.

A strict medication reconciliation match requires agreement with synthetic ground truth across:

- medication identity
- dose
- frequency
- route
- medication status

Precision, recall, and F1 are calculated from the predicted reconciled medication picture and expected medication picture.

---

# 4. Secondary Metrics

Additional metrics provide diagnostic information about system performance.

## Medication Identity F1

Measures whether medications are correctly identified and normalized.

## Dose Accuracy

Measures correctness of medication dose among evaluated medication records.

## Frequency Accuracy

Measures correctness of medication frequency.

## Route Accuracy

Measures correctness of administration route.

## Status Accuracy

Measures correctness of medication state, including states such as:

```text
current
recently_added
changed
discontinued
conflicting
uncertain
```

## Discrepancy F1

Measures detection of expected medication discrepancies.

## Interaction F1

Measures whether expected medication interaction findings are correctly detected.

---

# 5. Frozen Baseline — V0

V0 represents the simple deterministic baseline established before the final agent workflow.

Results:

| Metric | V0 |
|---|---:|
| Medication Reconciliation F1 | **0.6000** |
| Medication Identity F1 | 0.9667 |
| Dose Accuracy | 0.8621 |
| Frequency Accuracy | 1.0000 |
| Route Accuracy | 0.9655 |
| Status Accuracy | 0.6897 |
| Discrepancy F1 | 0.8000 |
| Interaction F1 | 0.0000 |

The primary baseline score was therefore:

```text
Medication Reconciliation F1 = 0.6000
```

V0 was frozen before subsequent agent improvements.

---

# 6. V1 — First Agent Pipeline

V1 introduced the first multi-agent medication reconstruction workflow.

Its primary result was:

```text
Medication Reconciliation F1 = 0.5902
```

This was lower than the V0 baseline:

```text
V0 = 0.6000
V1 = 0.5902
```

Absolute change:

```text
-0.0098
```

This experiment was intentionally preserved rather than removed from the project history.

## Interpretation

Adding agents did not automatically improve the user outcome.

The first pipeline exposed weaknesses in:

- repeated medication-event handling
- medication transition interpretation
- chronology
- source provenance
- conflicting medication reports

This failed experiment directly informed the next iteration.

---

# 7. V2 — Improved Medication Reconciliation

V2 focused on improving the reconciliation logic exposed by V1.

Development occurred through measured iterations.

## V2 Initial

```text
Medication Reconciliation F1 = 0.6885
```

## V2 Transition Refinement

Improved handling of medication transitions increased the score to:

```text
Medication Reconciliation F1 = 0.7213
```

## V2 Source-Aware Reconciliation

Preserving and reasoning over source provenance further increased the score to:

```text
Medication Reconciliation F1 = 0.7541
```

The final V2 evaluation was:

| Metric | V2 |
|---|---:|
| Medication Reconciliation F1 | **0.7541** |
| Medication Identity F1 | 0.9836 |
| Dose Accuracy | 0.9000 |
| Frequency Accuracy | 0.8667 |
| Route Accuracy | 1.0000 |
| Status Accuracy | 0.8333 |
| Discrepancy F1 | 0.7273 |
| Interaction F1 | 0.0000 |

V2 therefore improved the primary metric from:

```text
0.6000 → 0.7541
```

---

# 8. V3 — Reconcile First, Alert Second

V3 introduced the Medication Interaction Agent.

Importantly, interaction screening was added **after** medication reconciliation rather than being performed directly on raw medication mentions.

The V3 workflow is:

```text
Sources
   ↓
Intake & Extraction
   ↓
Medication Identity
   ↓
Timeline Reconstruction
   ↓
Medication Reconciliation
   ↓
Interaction Screening
   ↓
Human Review
```

The objective of V3 was twofold:

1. preserve the improved V2 reconciliation performance;
2. add measurable medication interaction detection.

---

# 9. Final V3 Results

The V3 evaluation completed successfully across all 20 synthetic cases.

```text
Completed: 20
Failed: 0
```

Final metrics:

| Metric | V3 |
|---|---:|
| Medication Reconciliation F1 | **0.7541** |
| Medication Identity F1 | **0.9836** |
| Dose Accuracy | **0.9000** |
| Frequency Accuracy | **0.8667** |
| Route Accuracy | **1.0000** |
| Status Accuracy | **0.8333** |
| Discrepancy F1 | **0.7273** |
| Interaction F1 | **1.0000** |

V3 preserved the final V2 reconciliation score:

```text
V2 Medication Reconciliation F1 = 0.7541
V3 Medication Reconciliation F1 = 0.7541
```

Therefore:

```text
V3 change vs V2 = 0.0000
```

The interaction capability was added without regression in the primary reconciliation metric.

---

# 10. Version Comparison

| Version | Reconciliation F1 | Interaction F1 | Main Change |
|---|---:|---:|---|
| V0 | 0.6000 | 0.0000 | Frozen deterministic baseline |
| V1 | 0.5902 | 0.0000 | First agent pipeline |
| V2 Initial | 0.6885 | 0.0000 | Improved reconciliation |
| V2 Transition | 0.7213 | 0.0000 | Better transition reasoning |
| V2 Final | 0.7541 | 0.0000 | Source-aware reconciliation |
| V3 | **0.7541** | **1.0000** | Post-reconciliation interaction screening |

---

# 11. Improvement Over Baseline

Final V3 reconciliation performance:

```text
0.7541
```

Frozen V0 baseline:

```text
0.6000
```

Absolute improvement:

```text
0.7541 - 0.6000 = +0.1541
```

Compared with the first agent implementation:

```text
0.7541 - 0.5902 = +0.1639
```

The final system therefore demonstrated measurable improvement over both the simple baseline and the initial agentic implementation.

---

# 12. Interaction Evaluation

The interaction capability was introduced in V3.

For the hackathon MVP, interaction screening uses a deterministic synthetic-approved knowledge base.

The representative interaction case contains:

```text
Warfarin
+
Trimethoprim-Sulfamethoxazole
```

Both medications must first survive reconciliation as screenable medication states.

The Interaction Agent then checks the normalized medication pair against the designated knowledge base.

The resulting finding contains:

- medication pair
- severity
- interaction type
- summary
- mechanism
- recommended review action
- verification status
- knowledge source
- supporting medication evidence
- human-review requirement

The final measured result was:

```text
Interaction F1 = 1.0000
```

This score applies only to the current synthetic evaluation set and limited hackathon interaction knowledge base.

It should not be interpreted as evidence of production-level drug-interaction coverage.

---

# 13. Representative Case — SYN-015

SYN-015 demonstrates the complete V3 workflow.

The reconciled medication picture contains:

```text
Trimethoprim-Sulfamethoxazole — current
Warfarin — current
```

Only after these medications are reconciled does interaction screening occur.

The Interaction Agent identifies the knowledge-supported pair and produces a high-severity potential interaction finding.

The finding includes:

```text
verification_status: knowledge_base_supported
needs_human_review: true
```

Medication evidence is also preserved from the underlying prescription source.

This case demonstrates the central MedRecon principle:

> Reconcile first. Alert second.

---

# 14. Human Review Evaluation Boundary

MedRecon does not treat an interaction finding as an autonomous clinical decision.

Potential medication-safety findings are surfaced for qualified review.

The system does not automatically:

- stop medication
- change medication
- change dose
- prescribe an alternative
- modify an order
- make a treatment decision

Interaction findings can therefore contain:

```text
needs_human_review: true
```

This provides an explicit safety boundary between automated medication intelligence and consequential clinical action.

---

# 15. Evaluation Artifacts

V3 pipeline outputs are stored under:

```text
outputs/evaluations/agent_v3/
```

Combined V3 predictions:

```text
outputs/evaluations/agent_v3_results.json
```

Final V3 evaluation metrics:

```text
outputs/evaluations/agent_v3_metrics.json
```

The evaluation can be reproduced using:

```bash
python scripts/run_agent_v3_pipeline.py
python scripts/run_agent_v3_evaluation.py
```

---

# 16. Evaluation Limitations

The current evaluation has important limitations.

### Synthetic Data

All cases are synthetic and do not represent clinical validation on real patient records.

### Small Dataset

The evaluation contains 20 cases.

This is appropriate for the hackathon experiment but insufficient for claims of broad clinical performance.

### Limited Medication Vocabulary

The MVP does not cover the full range of medications, synonyms, formulations, or clinical documentation patterns.

### Limited Interaction Knowledge Base

The interaction knowledge base is intentionally small and deterministic.

The measured:

```text
Interaction F1 = 1.0000
```

therefore represents performance on the current synthetic test set, not comprehensive real-world drug-interaction performance.

### Rule-Based Components

Several components use deterministic logic developed for the synthetic evaluation environment.

### No Clinical Outcome Evaluation

The project measures medication-reconstruction and safety-signal detection performance.

It does not measure patient outcomes.

---

# 17. Key Evaluation Finding

The strongest finding from the experiment was not that adding more agents automatically improved performance.

It did not.

The first agentic version performed slightly worse than the simple baseline:

```text
V0 = 0.6000
V1 = 0.5902
```

Performance improved only after the workflow became more deliberate about:

- medication transitions
- chronology
- source provenance
- conflicting evidence

The final result was:

```text
V3 Medication Reconciliation F1 = 0.7541
V3 Interaction F1 = 1.0000
```

This supports the project's core design insight:

> The most valuable agent in medication safety isn't necessarily the interaction checker; it is the system that determines which medications are actually current before safety screening begins.

---

## Conclusion

MedRecon AI improved its primary Medication Reconciliation F1 from:

```text
0.6000 → 0.7541
```

while subsequently adding interaction screening with:

```text
Interaction F1 = 1.0000
```

on the fixed 20-case synthetic benchmark.

The V1 regression was retained as evidence that agentic complexity alone was not sufficient.

The final V3 system instead combines specialized medication-processing agents, evidence provenance, deterministic safety screening, and explicit human-review checkpoints into an end-to-end medication reconciliation prototype.