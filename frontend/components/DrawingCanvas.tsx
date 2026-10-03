"use client";

import { useEffect, useRef, useState } from "react";
import { analyzeDrawing, ApiError, type DrawingPoint, type ModalityResult } from "@/lib/api";

// Internal canvas resolution. Points are sent in these coordinates, whatever the on-screen size.
const SIZE = 600;
const CENTER = SIZE / 2;
const TURNS = 3;
const MAX_RADIUS = 250;

function drawGuide(ctx: CanvasRenderingContext2D) {
  ctx.clearRect(0, 0, SIZE, SIZE);
  ctx.strokeStyle = "#c3ced6";
  ctx.lineWidth = 3;
  ctx.lineCap = "round";
  ctx.beginPath();
  const maxTheta = TURNS * 2 * Math.PI;
  for (let i = 0; i <= 600; i++) {
    const theta = (i / 600) * maxTheta;
    const r = (MAX_RADIUS * theta) / maxTheta;
    const x = CENTER + r * Math.cos(theta);
    const y = CENTER + r * Math.sin(theta);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
}

export default function DrawingCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const pointsRef = useRef<DrawingPoint[]>([]);
  const startRef = useRef<number | null>(null);
  const strokeRef = useRef(-1);
  const drawingRef = useRef(false);
  const inputTypeRef = useRef<string | undefined>(undefined);

  const [pointCount, setPointCount] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ModalityResult | null>(null);

  useEffect(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (ctx) drawGuide(ctx);
  }, []);

  const toCanvas = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * SIZE,
      y: ((e.clientY - rect.top) / rect.height) * SIZE,
    };
  };

  const record = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const { x, y } = toCanvas(e);
    if (startRef.current === null) startRef.current = e.timeStamp;
    pointsRef.current.push({
      x,
      y,
      t: e.timeStamp - startRef.current,
      stroke: strokeRef.current,
      // Mouse reports a constant 0.5 while pressed; only real pen/touch pressure is meaningful.
      ...(e.pointerType !== "mouse" && e.pressure > 0 ? { pressure: e.pressure } : {}),
    });
    setPointCount(pointsRef.current.length);
    return { x, y };
  };

  const onDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    drawingRef.current = true;
    strokeRef.current += 1;
    inputTypeRef.current = e.pointerType;
    setResult(null);
    setError(null);
    const { x, y } = record(e);
    const ctx = e.currentTarget.getContext("2d");
    if (ctx) {
      ctx.strokeStyle = "#12202e";
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      ctx.moveTo(x, y);
    }
  };

  const onMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!drawingRef.current) return;
    const { x, y } = record(e);
    const ctx = e.currentTarget.getContext("2d");
    if (ctx) {
      ctx.lineTo(x, y);
      ctx.stroke();
    }
  };

  const onUp = () => {
    drawingRef.current = false;
  };

  const clear = () => {
    pointsRef.current = [];
    startRef.current = null;
    strokeRef.current = -1;
    setPointCount(0);
    setResult(null);
    setError(null);
    const ctx = canvasRef.current?.getContext("2d");
    if (ctx) drawGuide(ctx);
  };

  const submit = async () => {
    setAnalyzing(true);
    setError(null);
    try {
      setResult(await analyzeDrawing(pointsRef.current, SIZE, inputTypeRef.current));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  const btn =
    "rounded-md px-5 py-2.5 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50";

  return (
    <div>
      <p className="text-muted">
        Trace the grey spiral from the centre outwards, slowly and steadily, using your finger, a
        stylus or the mouse. Try to stay on the line.
      </p>

      <canvas
        ref={canvasRef}
        width={SIZE}
        height={SIZE}
        onPointerDown={onDown}
        onPointerMove={onMove}
        onPointerUp={onUp}
        onPointerCancel={onUp}
        aria-label="Drawing area with a guide spiral to trace"
        className="mt-4 aspect-square w-full max-w-md touch-none rounded-lg border border-line bg-white"
      />

      <p className="mt-2 text-sm text-muted" aria-live="polite">
        {pointCount === 0 ? "Nothing drawn yet." : `${pointCount} points captured.`}
      </p>

      <div className="mt-3 flex flex-wrap gap-3">
        <button onClick={clear} disabled={analyzing} className={`${btn} border border-line bg-white text-ink hover:bg-paper`}>
          Clear
        </button>
        <button
          onClick={submit}
          disabled={analyzing || pointCount === 0}
          className={`${btn} bg-accent text-accent-ink hover:bg-[#0a5560]`}
        >
          {analyzing ? "Analysing…" : "Submit drawing"}
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-4 border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-900">
          {error}
        </p>
      )}
      {result && (
        <p className="mt-4 text-lg" role="status">
          Drawing screening signal: <strong>{Math.round(result.score * 100)}</strong> / 100
        </p>
      )}
    </div>
  );
}
