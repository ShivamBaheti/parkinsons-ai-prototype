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

type Scores = { voice?: number; drawing?: number; motion?: number };
const NAMES = ["voice", "drawing", "motion"] as const;

interface DrawingMeta {
  n_subjects?: number;
  class_counts?: { control: number; parkinson: number };
  evaluation?: { roc_auc: number; sensitivity: number; specificity: number; method: string };
  feature_importance?: { feature: string; importance: number }[];
  caveats?: string[];
}

function Bar({ value }: { value: number }) {
  return (
    <div className="mt-1 h-2 w-full rounded bg-line" role="img" aria-label={`${Math.round(value * 100)} out of 100`}>
      <div className="h-2 rounded bg-accent" style={{ width: `${Math.round(value * 100)}%` }} />
    </div>
  );
}

export default function ResultsView({ scores }: { scores: Scores }) {
  const hasScores = NAMES.some((n) => scores[n] !== undefined);
  const [result, setResult] = useState<ScreeningResponse | null>(null);
  const [info, setInfo] = useState<ModelInfoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(hasScores);

  const { voice, drawing, motion } = scores;
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

  const elevated = result.interpretation === "elevated_screening_signal";
  const drawingMeta = (info?.modalities.drawing?.metadata ?? null) as DrawingMeta | null;
  const topFeatures = drawingMeta?.feature_importance?.slice(0, 3).map((f) => f.feature.replaceAll("_", " "));

  return (
    <div className="mt-8">
      <h2 className="font-serif text-2xl font-medium">Overall screening score</h2>
      <p className="mt-2 text-5xl font-semibold" role="status">
        {result.screening_score} <span className="text-2xl font-normal text-muted">/ 100</span>
      </p>
      <Bar value={result.screening_score / 100} />
      <p className="mt-3">
        {elevated
          ? "Elevated screening signal: the combined model output is at or above 0.5. This is not a diagnosis. If you have any concerns, please speak to a healthcare professional."
          : "Lower screening signal: the combined model output is below 0.5. This does not rule anything out. If you have symptoms or concerns, please speak to a healthcare professional."}
      </p>

      <h2 className="mt-10 font-serif text-2xl font-medium">By test</h2>
      <ul className="mt-3 space-y-4">
        {NAMES.map((n) => {
          const v = result.modalities[n];
          return (
            <li key={n}>
              <span className="capitalize">{n}</span>:{" "}
              {v === null ? (
                <span className="text-muted">not tested (left out of the combined score)</span>
              ) : (
                <>
                  <strong>{Math.round(v * 100)}</strong> / 100
                  <span className="text-muted"> — contributes {result.fusion.contributions[n]} of the {result.screening_score} points</span>
                  <Bar value={v} />
                </>
              )}
            </li>
          );
        })}
      </ul>

      <h2 className="mt-10 font-serif text-2xl font-medium">How the scores were combined</h2>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
        <li>{result.fusion.note}</li>
        <li>The 0.5 threshold is each model&apos;s default, not a clinically validated cut-off.</li>
      </ul>

      {drawingMeta?.evaluation && result.modalities.drawing !== null && (
        <>
          <h2 className="mt-10 font-serif text-2xl font-medium">About the drawing model</h2>
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
            {drawingMeta.caveats?.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </>
      )}

      <p className="mt-10">
        <Link href="/screening" className="text-accent underline underline-offset-2">Back to screening</Link>
      </p>
    </div>
  );
}
