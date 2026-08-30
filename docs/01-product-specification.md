# MedRecon AI — Product Specification

## 1. Product Overview

MedRecon AI is a source-agnostic medication intelligence platform
designed to reconstruct a patient's medication picture from
fragmented healthcare information.

## 2. Problem

Medication information may be distributed across multiple sources,
including prescriptions, clinical notes, discharge documentation,
medication lists, patient-reported information, images, and
structured healthcare data.

These sources may contain duplicated, outdated, incomplete, or
conflicting medication information.

## 3. Product Goal

MedRecon aims to transform fragmented medication information into
an evidence-backed medication picture that can be reviewed by a
qualified human.

## 4. Core Capabilities

1. Medication information extraction
2. Medication identity resolution
3. Medication timeline reconstruction
4. Medication reconciliation
5. Discrepancy detection
6. Potential interaction screening
7. Evidence verification
8. Finding prioritization
9. Human review
10. Agent trajectory logging

## 5. Non-Goals

MedRecon does not:

- prescribe medications
- independently discontinue medications
- modify medication orders
- diagnose patients
- replace clinical judgment
- autonomously execute clinical actions

## 6. Primary User

Qualified healthcare professionals reviewing medication information.

## 7. Secondary Users

Patients and caregivers may use MedRecon to organize medication
information and identify issues that should be discussed with a
qualified healthcare professional.

## 8. Core Product Principle

Reconcile first. Alert second.

The system should establish the best-supported medication state
before performing medication-safety screening.