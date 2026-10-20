import { riskBand } from "@/lib/risk";

/** Score readout shown under each test: number out of 100 plus a Low / Medium / High chip. */
export default function ScoreLine({
  label,
  score,
}: {
  label: string;
  score: number;
}) {
  const pct = Math.round(score * 100);
  const b = riskBand(pct);
  return (
    <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-lg">
      <span>
        {label}: <strong>{pct}</strong> / 100
      </span>
      <span
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-sm font-semibold"
        style={{ background: b.tint, color: b.ink }}
      >
        <span className="h-2 w-2 rounded-full" style={{ background: b.color }} aria-hidden="true" />
        {b.label} signal
      </span>
    </p>
  );
}
