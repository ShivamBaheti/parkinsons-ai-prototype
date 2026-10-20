"use client";

import { useEffect, useState } from "react";
import { BANDS, riskBand } from "@/lib/risk";

// Semicircle from 180° (left) to 0° (right). Score 0 sits on the left, 100 on the right.
const CX = 150;
const CY = 150;
const R = 120;
const STROKE = 22;
const GAP = 1.2; // degrees of white space between bands

const point = (deg: number, r = R) => {
  const rad = (Math.PI * (180 - deg)) / 180;
  return { x: CX + r * Math.cos(rad), y: CY - r * Math.sin(rad) };
};

const arc = (from: number, to: number) => {
  const a = point(from);
  const b = point(to);
  return `M ${a.x.toFixed(2)} ${a.y.toFixed(2)} A ${R} ${R} 0 0 1 ${b.x.toFixed(2)} ${b.y.toFixed(2)}`;
};

const scoreToDeg = (s: number) => (Math.min(100, Math.max(0, s)) / 100) * 180;

const EDGES = [0, 30, 50, 100];

export default function RiskGauge({ score }: { score: number }) {
  const band = riskBand(score);
  const [shown, setShown] = useState(0);

  // The needle sweeps from zero to the score once, when the result appears.
  useEffect(() => {
    const id = requestAnimationFrame(() => setShown(score));
    return () => cancelAnimationFrame(id);
  }, [score]);

  const needleLength = R - STROKE / 2 - 10;

  return (
    <figure className="mx-auto w-full max-w-sm">
      <svg
        viewBox="0 0 300 180"
        role="img"
        aria-label={`${band.label} screening signal, score ${score} out of 100`}
        className="w-full"
      >
        {BANDS.map((b, i) => (
          <path
            key={b.key}
            d={arc(
              scoreToDeg(EDGES[i]) + (i === 0 ? 0 : GAP),
              scoreToDeg(EDGES[i + 1]) - (i === BANDS.length - 1 ? 0 : GAP),
            )}
            fill="none"
            stroke={b.color}
            strokeWidth={STROKE}
            strokeLinecap="butt"
            opacity={b.key === band.key ? 1 : 0.28}
            style={{ transition: "opacity 600ms ease 400ms" }}
          />
        ))}

        {/* Drawn pointing at 0, then rotated clockwise around the hub to the score. */}
        <g
          className="gauge-needle"
          style={{ transform: `rotate(${scoreToDeg(shown)}deg)`, transformOrigin: `${CX}px ${CY}px` }}
        >
          <line x1={CX} y1={CY} x2={CX - needleLength} y2={CY} stroke="var(--ink)" strokeWidth={4} strokeLinecap="round" />
        </g>
        <circle cx={CX} cy={CY} r={9} fill="var(--ink)" />
        <circle cx={CX} cy={CY} r={3.5} fill="var(--paper)" />

        <text x={CX - R} y={CY + 22} textAnchor="middle" fontSize="12" fill="var(--muted)">0</text>
        <text x={CX + R} y={CY + 22} textAnchor="middle" fontSize="12" fill="var(--muted)">100</text>
      </svg>

      <figcaption className="-mt-2 text-center">
        <span
          className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-lg font-semibold"
          style={{ background: band.tint, color: band.ink }}
        >
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: band.color }} aria-hidden="true" />
          {band.label} signal
        </span>
        <span className="mt-3 block font-serif text-5xl font-medium tracking-tight">
          {score}
          <span className="ml-1 text-xl font-normal text-muted">/ 100</span>
        </span>
      </figcaption>
    </figure>
  );
}
