"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  analyzeScreening,
  ApiError,
  getModelInfo,
  type ModelInfoResponse,
  type ScreeningResponse,
} from "@/lib/api";
import { BANDS, riskBand } from "@/lib/risk";
import RiskGauge from "@/components/RiskGauge";
import SpiralReplay from "@/components/SpiralReplay";
import WhyScore from "@/components/WhyScore";
import { useStoredDrawing } from "@/lib/spiral";

type Scores = { voice?: number; drawing?: number; motion?: number };
const NAMES = ["voice", "drawing", "motion"] as const;

interface DrawingMeta {
  n_subjects?: number;
  class_counts?: { control: number; parkinson: number };
  evaluation?: { roc_auc: number; sensitivity: number; specificity: number; method: string };
  feature_importance?: { feature: string; importance: number }[];
  caveats?: string[];
  excluded_features?: { features: string[]; reason: string };
}

const FEATURE_LABELS: Record<string, string> = {
  radial_residual_rms: "deviation from an ideal spiral",
  speed_cv: "speed variability",
  pause_fraction: "time spent paused",
  heading_change_std: "variability of direction changes",
  turns: "number of turns",
  duration_s: "drawing duration",
  path_length: "path length",
};
const label = (f: string) => FEATURE_LABELS[f] ?? f.replaceAll("_", " ");

function Bar({ value, muted = false }: { value: number; muted?: boolean }) {
  const pct = Math.round(value * 100);
  const color = muted ? "#8a99a6" : riskBand(pct).color;
  return (
    <div className="relative mt-2 h-2.5 w-full rounded-full bg-line" role="img" aria-label={`${pct} out of 100`}>
      <div className="h-2.5 rounded-full" style={{ width: `${pct}%`, background: color }} />
      {[30, 50].map((t) => (
        <span key={t} className="absolute top-[-3px] h-[16px] w-px bg-ink/25" style={{ left: `${t}%` }} aria-hidden="true" />
      ))}
    </div>
  );
}

function Chip({ text, color, tint, ink }: { text: string; color: string; tint: string; ink: string }) {
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-semibold"
      style={{ background: tint, color: ink }}
    >
      <span className="h-2 w-2 rounded-full" style={{ background: color }} aria-hidden="true" />
      {text}
    </span>
  );
}

export default function ResultsView({ scores }: { scores: Scores }) {
  const hasScores = NAMES.some((n) => scores[n] !== undefined);
  const [result, setResult] = useState<ScreeningResponse | null>(null);
  const [info, setInfo] = useState<ModelInfoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(hasScores);

  const { voice, drawing, motion } = scores;
  const stored = useStoredDrawing(drawing);

  // Open the collapsed details when printing so the printout is complete.
  useEffect(() => {
    const open = () => document.querySelectorAll("details").forEach((d) => (d.open = true));
    window.addEventListener("beforeprint", open);
    return () => window.removeEventListener("beforeprint", open);
  }, []);
  useEffect(() => {
    if (voice === undefined && drawing === undefined && motion === undefined) return;
    analyzeScreening({ voice, drawing, motion })
      .then(setResult)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again."),
      )
      .finally(() => setLoading(false));
    getModelInfo().then(setInfo).catch(() => setInfo(null)); // model details are optional
  }, [voice, drawing, motion]);

  if (!hasScores) {
    return (
      <p className="mt-8">
        No test scores were provided.{" "}
        <Link href="/screening" className="text-accent underline underline-offset-2">Go to the screening page</Link>{" "}
        and complete at least one test.
      </p>
    );
  }
  if (loading) return <p className="mt-8 text-muted" role="status">Combining results…</p>;
  if (error || !result) {
    return (
      <p role="alert" className="mt-8 border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-900">
        {error ?? "No result was returned."}
      </p>
    );
  }

  const excluded = result.fusion.modalities_excluded ?? [];
  const elevated = result.interpretation === "elevated_screening_signal";
  const drawingMeta = (info?.modalities.drawing?.metadata ?? null) as DrawingMeta | null;
  const topFeatures = drawingMeta?.feature_importance?.slice(0, 3).map((f) => label(f.feature));

  const band = riskBand(result.screening_score);
  const usedNames = result.fusion.modalities_used.join(" and ");

  return (
    <div className="mt-8">
      <div className="mb-4 flex items-center justify-between gap-3">
        <p className="text-sm text-muted">{new Date().toLocaleDateString(undefined, { dateStyle: "long" })}</p>
        <button
          onClick={() => window.print()}
          className="no-print rounded-lg border border-line bg-white px-4 py-2 text-sm font-semibold text-accent shadow-sm transition-colors hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Print result
        </button>
      </div>
      <section
        className="rounded-2xl border px-6 py-8 sm:px-10"
        style={{ borderColor: `${band.color}55`, background: `linear-gradient(180deg, ${band.tint} 0%, #ffffff 70%)` }}
        aria-labelledby="overall-heading"
      >
        <h2 id="overall-heading" className="text-center font-serif text-2xl font-medium">
          Overall screening signal
        </h2>
        <div className="mt-4" role="status">
          <RiskGauge score={result.screening_score} />
        </div>
        <p className="mx-auto mt-5 max-w-md text-center text-lg leading-snug">{band.summary}</p>
        <p className="mx-auto mt-2 max-w-md text-center text-sm text-muted">
          Based on {usedNames} only. {elevated ? "The combined model output is at or above 0.5." : "The combined model output is below 0.5."}{" "}
          If you have symptoms or concerns, please speak to a healthcare professional.
        </p>
        <p className="mx-auto mt-3 max-w-md text-center text-xs font-semibold text-muted">
          Research prototype. Not a medical diagnosis.
        </p>
      </section>

      {stored?.contributions && stored.features && (
        <WhyScore
          contributions={stored.contributions}
          baseline={stored.baseline}
          features={stored.features}
          score={Math.round(stored.score * 100)}
        />
      )}

      {stored && (
        <div className="mt-10">
          <SpiralReplay points={stored.points} />
        </div>
      )}

      <h2 className="mt-10 font-serif text-2xl font-medium">What the levels mean</h2>
      <ul className="mt-3 space-y-2">
        {BANDS.map((b) => (
          <li key={b.key} className="flex items-center gap-3">
            <Chip text={b.label} color={b.color} tint={b.tint} ink={b.ink} />
            <span className="text-muted">Score {b.range}</span>
            {b.key === band.key && <span className="text-sm font-semibold">← your result</span>}
          </li>
        ))}
      </ul>
      <p className="mt-2 text-sm text-muted">
        Only the 50 boundary comes from the model&apos;s default threshold. The Low and Medium split is a
        presentation choice, and none of these levels are clinically validated.
      </p>

      <h2 className="mt-10 font-serif text-2xl font-medium">By test</h2>
      <ul className="mt-3 space-y-5">
        {NAMES.map((n) => {
          const v = result.modalities[n];
          const isExcluded = excluded.includes(n);
          const b = v === null ? null : riskBand(Math.round(v * 100));
          return (
            <li key={n}>
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                <span className="font-semibold capitalize">{n}</span>
                {v === null ? (
                  <span className="text-muted">Not tested</span>
                ) : (
                  <>
                    <span>
                      <strong>{Math.round(v * 100)}</strong> / 100
                    </span>
                    {b && <Chip text={`${b.label} signal`} color={b.color} tint={b.tint} ink={b.ink} />}
                  </>
                )}
              </div>
              {v !== null && <Bar value={v} />}
              <p className="mt-1.5 text-sm text-muted">
                {v === null
                  ? "Left out of the combined score."
                  : isExcluded
                    ? "Not counted in the overall score."
                    : result.fusion.modalities_used.length === 1
                      ? "The only test in the combined score."
                      : `Contributes ${result.fusion.contributions[n]} of the ${result.screening_score} points.`}
              </p>
            </li>
          );
        })}
      </ul>

      <details className="group mt-10 rounded-xl border border-line bg-white px-5 py-4">
        <summary className="cursor-pointer list-none font-serif text-2xl font-medium marker:hidden focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-accent">
          <span className="mr-2 inline-block text-accent transition-transform group-open:rotate-90" aria-hidden="true">›</span>
          Method and model details
        </summary>
      <h2 className="mt-6 font-serif text-xl font-medium">How the scores were combined</h2>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
        <li>{result.fusion.note}</li>
        <li>The 0.5 threshold is each model&apos;s default, not a clinically validated cut-off.</li>
      </ul>

      {drawingMeta?.evaluation && result.modalities.drawing !== null && (
        <>
          <h2 className="mt-8 font-serif text-xl font-medium">About the drawing model</h2>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
            <li>
              Trained on {drawingMeta.n_subjects} people ({drawingMeta.class_counts?.control} controls,{" "}
              {drawingMeta.class_counts?.parkinson} with Parkinson&apos;s) using stylus-on-tablet spirals.
            </li>
            <li>
              Cross-validated (repeated 5-fold, one row per person): ROC-AUC {drawingMeta.evaluation.roc_auc},
              sensitivity {drawingMeta.evaluation.sensitivity}, specificity {drawingMeta.evaluation.specificity}.
              Roughly 1 in {Math.round(1 / (1 - drawingMeta.evaluation.sensitivity))} people with Parkinson&apos;s in
              that data would be missed.
            </li>
            {topFeatures && (
              <li>
                Across the whole model, {topFeatures.join(", ")} had a relatively high contribution to its output.
              </li>
            )}
            {drawingMeta.excluded_features && (
              <li>
                Left out on purpose: {drawingMeta.excluded_features.features.map(label).join(", ")}. {drawingMeta.excluded_features.reason}
              </li>
            )}
            {drawingMeta.caveats?.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </>
      )}

      </details>

      <p className="mt-10">
        <Link
          href="/screening"
          className="inline-block rounded-lg border border-line bg-white px-5 py-2.5 font-semibold text-accent transition-colors hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Back to screening
        </Link>
      </p>
    </div>
  );
}
