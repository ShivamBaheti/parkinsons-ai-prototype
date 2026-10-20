"use client";

import Link from "next/link";
import { useState } from "react";
import DrawingCanvas from "@/components/DrawingCanvas";
import MotionUploader from "@/components/MotionUploader";
import VoiceRecorder from "@/components/VoiceRecorder";

type Scores = { voice: number | null; drawing: number | null; motion: number | null };

const TONES = {
  demo: "bg-line text-muted",
  working: "bg-[#e4f4ec] text-[#124d33]",
  unavailable: "bg-[#fdf0d6] text-[#6b4204]",
} as const;

function StepHeader({
  n,
  title,
  status,
  tone,
  complete,
}: {
  n: number;
  title: string;
  status: string;
  tone: keyof typeof TONES;
  complete: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <span
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
          complete ? "bg-accent text-accent-ink" : "border border-line bg-white text-muted"
        }`}
        aria-hidden="true"
      >
        {complete ? "✓" : n}
      </span>
      <h2 className="font-serif text-2xl font-medium">
        {title}
        {complete && <span className="sr-only"> (completed)</span>}
      </h2>
      <span className={`rounded-full px-2.5 py-0.5 text-sm font-semibold ${TONES[tone]}`}>{status}</span>
    </div>
  );
}

export default function ScreeningFlow() {
  const [scores, setScores] = useState<Scores>({ voice: null, drawing: null, motion: null });
  const set = (key: keyof Scores) => (score: number | null) => setScores((s) => ({ ...s, [key]: score }));

  const done = (Object.keys(scores) as (keyof Scores)[]).filter((k) => scores[k] !== null);
  const query = new URLSearchParams(done.map((k) => [k, String(scores[k])])).toString();

  return (
    <>
      <section className="mt-10">
        <StepHeader n={1} title="Voice" status="Optional" tone="demo" complete={scores.voice !== null} />
                <div className="mt-4"><VoiceRecorder onScore={set("voice")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <StepHeader n={2} title="Drawing" status="Working model" tone="working" complete={scores.drawing !== null} />
        <p className="mt-2 text-sm text-muted">Prototype model, trained on stylus-and-tablet spirals (not yet validated for mouse or touch).</p>
        <div className="mt-4"><DrawingCanvas onScore={set("drawing")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <StepHeader n={3} title="Motion" status="Not available yet" tone="unavailable" complete={scores.motion !== null} />
        <p className="mt-2 text-sm text-muted">Files are checked, but no motion model has been trained, so no score is produced.</p>
        <div className="mt-4"><MotionUploader onScore={set("motion")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <h2 className="font-serif text-2xl font-medium">Combined result</h2>
        <p className="mt-3 text-muted">
          Tests completed: {done.length === 0 ? "none yet" : done.join(", ")}. You can view the combined
          result with any of the tests; tests you skip are left out.
        </p>
        {done.length > 0 ? (
          <Link
            href={`/results?${query}`}
            className="mt-4 inline-block rounded-lg bg-accent px-6 py-3 font-semibold text-accent-ink shadow-sm transition-colors hover:bg-[#0a5560] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            See your risk level
          </Link>
        ) : (
          <p className="mt-4 text-sm text-muted">Complete at least one test to enable this.</p>
        )}
      </section>
    </>
  );
}
