# MedRecon AI — Architecture

## Architecture Principle

MedRecon uses specialized agents with narrow responsibilities
rather than a single general-purpose agent performing the entire
workflow.

## High-Level Flow

Input Sources
    ↓
Ingestion
    ↓
Extraction Agent
    ↓
Medication Identity Agent
    ↓
Timeline Agent
    ↓
Reconciliation Agent
    ↓
Discrepancy Agent
    ↓
Interaction Agent
    ↓
Verification Agent
    ↓
Prioritization Agent
    ↓
Evidence-backed Report
    ↓
Human Review

## Design Rationale

Each agent has a defined responsibility and structured input/output
contract.

This allows individual components to be evaluated independently,
debugged independently, and replaced without redesigning the entire
system.

## Human Oversight

MedRecon surfaces findings for qualified human review rather than
autonomously executing consequential clinical actions.