"use client";

import { useState } from "react";
import ScoreLine from "@/components/ScoreLine";
import { analyzeMotion, ApiError, type ModalityResult } from "@/lib/api";

export default function MotionUploader({ onScore }: { onScore?: (score: number | null) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ModalityResult | null>(null);

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
    setError(null);
    setResult(null);
    onScore?.(null);
  };

  const analyze = async () => {
    if (!file) return;
    setAnalyzing(true);
    setError(null);
    try {
      const r = await analyzeMotion(file);
      setResult(r);
      onScore?.(r.score);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const btn =
    "rounded-lg px-5 py-2.5 font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50";

  return (
    <div>
      <p className="text-muted">
        Upload a CSV recorded by a phone or smartwatch motion-sensor app while the hand is held
        still for at least 10 seconds. Motion collection in the browser is not supported.
      </p>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted marker:text-accent">
        <li>
          Required columns: timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
        </li>
        <li>Timestamp in seconds (milliseconds are detected), at least 20 samples per second</li>
        <li>Acceleration in g or m/s² (detected), gyroscope in rad/s</li>
      </ul>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <label className={`${btn} cursor-pointer border border-line bg-white text-ink hover:bg-paper`}>
          Choose CSV file
          <input type="file" accept=".csv,text/csv" className="sr-only" onChange={onFile} disabled={analyzing} />
        </label>
        {file && <span className="text-sm text-muted">{file.name}</span>}
      </div>

      {file && (
        <button
          onClick={analyze}
          disabled={analyzing}
          className={`${btn} mt-4 bg-accent text-accent-ink hover:bg-[#0a5560]`}
        >
          {analyzing ? "Analysing…" : "Analyse motion data"}
        </button>
      )}

      {error && (
        <p role="alert" className="mt-4 border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-900">
          {error}
        </p>
      )}
      {result && (
        <div className="mt-4" role="status">
          <ScoreLine label="Motion screening signal" score={result.score} />
        </div>
      )}
    </div>
  );
}
