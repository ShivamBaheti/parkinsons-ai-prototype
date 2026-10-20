"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { guidePoints, deviations, SIZE, type StoredPoint } from "@/lib/spiral";

const PLAY_MS = 9000; // long drawings are sped up to replay in about this long
const CLOSE_PX = 15; // "on the guide" threshold, in canvas pixels

// Teal on the guide, amber when drifting, coral when far off (tuned for the dark panel).
const STOPS: [number, [number, number, number]][] = [
  [0, [45, 212, 191]],
  [18, [251, 191, 36]],
  [36, [248, 113, 113]],
];
function colour(d: number) {
  for (let i = 1; i < STOPS.length; i++) {
    const [d0, c0] = STOPS[i - 1];
    const [d1, c1] = STOPS[i];
    if (d <= d1) {
      const f = Math.max(0, (d - d0) / (d1 - d0));
      return `rgb(${c0.map((v, k) => Math.round(v + (c1[k] - v) * f)).join(",")})`;
    }
  }
  return `rgb(${STOPS[STOPS.length - 1][1].join(",")})`;
}

export default function SpiralReplay({ points }: { points: StoredPoint[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const guide = useMemo(() => guidePoints(), []);
  const devs = useMemo(() => deviations(points), [points]);
  const duration = points[points.length - 1][2];
  const speed = Math.max(1, duration / PLAY_MS);

  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [pos, setPos] = useState(reduced ? duration : 0);
  const [playing, setPlaying] = useState(!reduced);
  const posRef = useRef(pos);
  useEffect(() => {
    posRef.current = pos;
  }, [pos]);

  const close = Math.round((devs.filter((d) => d <= CLOSE_PX).length / devs.length) * 100);

  const draw = useCallback(
    (upTo: number) => {
      const ctx = canvasRef.current?.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, SIZE, SIZE);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      ctx.strokeStyle = "rgba(255,255,255,0.2)";
      ctx.lineWidth = 3;
      ctx.beginPath();
      guide.forEach((g, i) => (i === 0 ? ctx.moveTo(g.x, g.y) : ctx.lineTo(g.x, g.y)));
      ctx.stroke();

      let head = -1;
      ctx.lineWidth = 4.5;
      for (let i = 1; i < points.length && points[i][2] <= upTo; i++) {
        head = i;
        if (points[i][3] !== points[i - 1][3]) continue; // new stroke: do not join across the lift
        ctx.strokeStyle = colour((devs[i] + devs[i - 1]) / 2);
        ctx.beginPath();
        ctx.moveTo(points[i - 1][0], points[i - 1][1]);
        ctx.lineTo(points[i][0], points[i][1]);
        ctx.stroke();
      }
      if (head >= 0 && upTo < duration) {
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(points[head][0], points[head][1], 7, 0, Math.PI * 2);
        ctx.fill();
      }
    },
    [guide, points, devs, duration],
  );

  useEffect(() => draw(pos), [pos, draw]);

  // Advance the replay with the animation clock.
  useEffect(() => {
    if (!playing) return;
    let raf = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const next = Math.min(duration, posRef.current + (now - last) * speed);
      last = now;
      setPos(next);
      if (next >= duration) setPlaying(false);
      else raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, duration, speed]);

  // Printing always shows the finished spiral.
  useEffect(() => {
    const before = () => draw(duration);
    const after = () => draw(posRef.current);
    window.addEventListener("beforeprint", before);
    window.addEventListener("afterprint", after);
    return () => {
      window.removeEventListener("beforeprint", before);
      window.removeEventListener("afterprint", after);
    };
  }, [draw, duration]);

  const toggle = () => {
    if (pos >= duration) setPos(0);
    setPlaying((p) => (pos >= duration ? true : !p));
  };

  return (
    <section className="replay-panel rounded-2xl bg-[#0f1b27] p-5 text-white sm:p-7" aria-labelledby="replay-heading">
      <h2 id="replay-heading" className="font-serif text-2xl font-medium">
        Your spiral, replayed
      </h2>
      <p className="mt-1 text-sm text-white/70">
        The grey line is the guide. Your line is coloured by how far it was from the guide at each moment.
      </p>

      <canvas
        ref={canvasRef}
        width={SIZE}
        height={SIZE}
        role="img"
        aria-label={`Replay of your spiral. ${close}% of your line stayed close to the guide.`}
        className="mx-auto mt-4 block aspect-square w-full max-w-md"
      />

      <div className="no-print mt-4 flex items-center gap-3">
        <button
          onClick={toggle}
          className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-[#0f1b27] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
        >
          {playing ? "Pause" : pos >= duration ? "Replay" : "Play"}
        </button>
        <input
          type="range"
          min={0}
          max={Math.round(duration)}
          value={Math.round(pos)}
          onChange={(e) => {
            setPlaying(false);
            setPos(Number(e.target.value));
          }}
          aria-label="Replay position"
          className="h-2 flex-1 accent-teal-300"
        />
        <span className="w-14 text-right text-sm tabular-nums text-white/70">{(pos / 1000).toFixed(1)}s</span>
      </div>
      {speed > 1.05 && <p className="no-print mt-1 text-xs text-white/50">Replayed at {speed.toFixed(1)}× speed.</p>}

      <div className="mt-4 flex items-center gap-3 text-xs text-white/70" aria-hidden="true">
        <span>On the guide</span>
        <span
          className="h-2 flex-1 rounded-full"
          style={{ background: `linear-gradient(90deg, ${colour(0)}, ${colour(18)}, ${colour(40)})` }}
        />
        <span>Far from the guide</span>
      </div>
      <p className="mt-4 text-lg">
        <strong>{close}%</strong> of your line stayed close to the guide.
      </p>
    </section>
  );
}
