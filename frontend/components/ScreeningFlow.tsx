"use client";

import Link from "next/link";
import { useState } from "react";
import DrawingCanvas from "@/components/DrawingCanvas";
import MotionUploader from "@/components/MotionUploader";
import VoiceRecorder from "@/components/VoiceRecorder";

type Scores = { voice: number | null; drawing: number | null; motion: number | null };

export default function ScreeningFlow() {
  const [scores, setScores] = useState<Scores>({ voice: null, drawing: null, motion: null });
  const set = (key: keyof Scores) => (score: number | null) => setScores((s) => ({ ...s, [key]: score }));

  const done = (Object.keys(scores) as (keyof Scores)[]).filter((k) => scores[k] !== null);
  const query = new URLSearchParams(done.map((k) => [k, String(scores[k])])).toString();

  return (
    <>
      <section className="mt-10">
        <h2 className="font-serif text-2xl font-medium">Step 1 — Voice</h2>
        <div className="mt-4"><VoiceRecorder onScore={set("voice")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <h2 className="font-serif text-2xl font-medium">Step 2 — Drawing</h2>
        <div className="mt-4"><DrawingCanvas onScore={set("drawing")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <h2 className="font-serif text-2xl font-medium">Step 3 — Motion</h2>
        <div className="mt-4"><MotionUploader onScore={set("motion")} /></div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <h2 className="font-serif text-2xl font-medium">Combined result</h2>
        <p className="mt-3 text-muted">
          Tests completed: {done.length === 0 ? "none yet" : done.join(", ")}. You can view the combined
          result with any of the tests; tests you skip are left out. The voice result is a demonstration
          and is not included in the combined score, so complete the drawing or motion test as well.
        </p>
        {done.length > 0 ? (
          <Link
            href={`/results?${query}`}
            className="mt-4 inline-block rounded-md bg-accent px-5 py-2.5 font-semibold text-accent-ink hover:bg-[#0a5560] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            View combined result
          </Link>
        ) : (
          <p className="mt-4 text-sm text-muted">Complete at least one test to enable this.</p>
        )}
      </section>
    </>
  );
}
