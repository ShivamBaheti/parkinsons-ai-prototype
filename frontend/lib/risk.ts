/**
 * Maps a 0-100 screening score to a plain-language signal level.
 * The 50 boundary matches the backend threshold (0.5 = "elevated").
 * The Low/Medium split at 30 is a presentation choice, not a clinical cut-off.
 */
export type RiskKey = "low" | "medium" | "high";

export interface RiskBand {
  key: RiskKey;
  label: string;
  range: string;
  color: string; // solid colour for arcs, bars and dots
  tint: string; // soft background
  ink: string; // readable text colour on the tint
  summary: string;
}

export const BANDS: RiskBand[] = [
  {
    key: "low",
    label: "Low",
    range: "0 – 29",
    color: "#1f8a5b",
    tint: "#e4f4ec",
    ink: "#124d33",
    summary:
      "The models found few of the patterns they associate with Parkinson's. This does not rule anything out.",
  },
  {
    key: "medium",
    label: "Medium",
    range: "30 – 49",
    color: "#d98a0b",
    tint: "#fdf0d6",
    ink: "#6b4204",
    summary:
      "The models found some patterns they associate with Parkinson's, but not enough to call the signal elevated.",
  },
  {
    key: "high",
    label: "High",
    range: "50 – 100",
    color: "#c4432f",
    tint: "#fbe4df",
    ink: "#7a2316",
    summary:
      "The models found several patterns they associate with Parkinson's. This is not a diagnosis, but it is worth discussing with a doctor.",
  },
];

export function riskBand(score: number): RiskBand {
  if (score >= 50) return BANDS[2];
  if (score >= 30) return BANDS[1];
  return BANDS[0];
}
