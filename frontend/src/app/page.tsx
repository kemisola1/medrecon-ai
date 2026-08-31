"use client";

import { useState } from "react";

type Medication = {
  medication_name?: string;
  dose?: string | null;
  frequency?: string | null;
  route?: string | null;
  status?: string | null;
  needs_verification?: boolean;
};

type Discrepancy = {
  medication_name?: string;
  type?: string;
  severity?: string;
  description?: string;
  verification_status?: string;
};

type Interaction = {
  drug_a?: string;
  drug_b?: string;
  severity?: string;
  summary?: string;
  recommended_action?: string;
  needs_human_review?: boolean;
};

type PipelineResult = {
  case_id?: string;
  status?: string;
  medications?: Medication[];
  discrepancies?: Discrepancy[];
  interactions?: Interaction[];
  pipeline_version?: string;
};

const demoCase = {
  case_id: "DEMO-001",
  sources: [
    {
      source_id: "DEMO-SRC-001",
      type: "prescription",
      source_date: "2026-08-28",
      text: "Warfarin 5 mg orally once daily. Trimethoprim-sulfamethoxazole 160/800 mg orally twice daily.",
    },
  ],
};

export default function Home() {
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runDemo() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/reconcile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(demoCase),
      });

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the MedRecon backend."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">
        <header className="mb-12">
          <div className="mb-4 inline-flex rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-2 text-sm text-violet-300">
            Medication Intelligence Layer
          </div>

          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            MedRecon AI
          </h1>

          <p className="mt-4 max-w-3xl text-lg text-slate-300">
            Reconcile fragmented medication information, identify discrepancies,
            screen potential medication interactions, and surface evidence for
            qualified human review.
          </p>

          <p className="mt-3 text-sm text-slate-400">
            Reconcile first. Alert second.
          </p>
        </header>

        <section className="mb-10 grid gap-6 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Reconciliation F1</p>
            <p className="mt-2 text-3xl font-semibold">0.7541</p>
            <p className="mt-2 text-sm text-slate-500">
              Final V3 medication reconciliation score
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Interaction F1</p>
            <p className="mt-2 text-3xl font-semibold">1.0000</p>
            <p className="mt-2 text-sm text-slate-500">
              Deterministic interaction screening
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Evaluation Cases</p>
            <p className="mt-2 text-3xl font-semibold">20</p>
            <p className="mt-2 text-sm text-slate-500">
              Synthetic medication reconciliation cases
            </p>
          </div>
        </section>

        <section className="mb-10 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
            <div>
              <h2 className="text-2xl font-semibold">Demo medication case</h2>

              <p className="mt-2 max-w-3xl text-slate-400">
                Warfarin and trimethoprim-sulfamethoxazole are provided in the
                same prescription source. MedRecon will reconcile the medication
                picture first, then screen the active medications against its
                approved synthetic interaction knowledge base.
              </p>
            </div>

            <button
              onClick={runDemo}
              disabled={loading}
              className="rounded-xl bg-violet-600 px-6 py-3 font-medium transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Running MedRecon..." : "Run MedRecon"}
            </button>
          </div>
        </section>

        {error && (
          <section className="mb-8 rounded-2xl border border-red-500/30 bg-red-500/10 p-5 text-red-200">
            <p className="font-semibold">Unable to run MedRecon</p>
            <p className="mt-2 text-sm">{error}</p>
          </section>
        )}

        {result && (
          <div className="space-y-8">
            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="text-2xl font-semibold">
                  Reconciled Medication Picture
                </h2>

                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
                  {result.pipeline_version ?? "V3"}
                </span>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                {(result.medications ?? []).map((medication, index) => (
                  <div
                    key={`${medication.medication_name}-${index}`}
                    className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold">
                          {medication.medication_name ?? "Unknown medication"}
                        </h3>

                        <p className="mt-1 text-sm text-slate-400">
                          {medication.dose ?? "Dose unknown"} ·{" "}
                          {medication.frequency ?? "Frequency unknown"} ·{" "}
                          {medication.route ?? "Route unknown"}
                        </p>
                      </div>

                      <span className="rounded-full bg-sky-500/10 px-3 py-1 text-xs uppercase tracking-wide text-sky-300">
                        {medication.status ?? "unknown"}
                      </span>
                    </div>

                    {medication.needs_verification && (
                      <p className="mt-4 text-sm text-amber-300">
                        Requires verification
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-2xl font-semibold">Discrepancies</h2>

              {(result.discrepancies ?? []).length === 0 ? (
                <p className="mt-4 text-slate-400">
                  No medication discrepancies detected in this case.
                </p>
              ) : (
                <div className="mt-6 space-y-4">
                  {(result.discrepancies ?? []).map((item, index) => (
                    <div
                      key={`${item.medication_name}-${index}`}
                      className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-5"
                    >
                      <p className="font-semibold">
                        {item.medication_name ?? "Medication discrepancy"}
                      </p>

                      <p className="mt-1 text-sm text-amber-300">
                        {item.type ?? "discrepancy"} ·{" "}
                        {item.severity ?? "severity unspecified"}
                      </p>

                      {item.description && (
                        <p className="mt-3 text-sm text-slate-300">
                          {item.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-2xl border border-red-500/20 bg-slate-900 p-6">
              <h2 className="text-2xl font-semibold">
                Potential Interaction Findings
              </h2>

              {(result.interactions ?? []).length === 0 ? (
                <p className="mt-4 text-slate-400">
                  No knowledge-supported interaction was detected.
                </p>
              ) : (
                <div className="mt-6 space-y-4">
                  {(result.interactions ?? []).map((interaction, index) => (
                    <div
                      key={`${interaction.drug_a}-${interaction.drug_b}-${index}`}
                      className="rounded-xl border border-red-500/30 bg-red-500/10 p-5"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <p className="text-lg font-semibold">
                          {interaction.drug_a} + {interaction.drug_b}
                        </p>

                        <span className="rounded-full bg-red-500/20 px-3 py-1 text-xs font-medium uppercase tracking-wide text-red-200">
                          {interaction.severity ?? "potential interaction"}
                        </span>
                      </div>

                      {interaction.summary && (
                        <p className="mt-4 text-slate-200">
                          {interaction.summary}
                        </p>
                      )}

                      {interaction.recommended_action && (
                        <p className="mt-3 text-sm text-slate-400">
                          {interaction.recommended_action}
                        </p>
                      )}

                      {interaction.needs_human_review && (
                        <div className="mt-4 rounded-lg border border-amber-500/20 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
                          Qualified clinician or pharmacist review required.
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">Safety boundary</h2>

              <p className="mt-3 text-sm leading-6 text-slate-400">
                MedRecon AI provides medication reconciliation and
                decision-support findings only. It does not prescribe,
                discontinue, change medication orders, or autonomously make
                clinical decisions. Consequential findings require qualified
                human review.
              </p>
            </section>
          </div>
        )}
      </div>
    </main>
  );
}