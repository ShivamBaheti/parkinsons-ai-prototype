import { useMemo, useSyncExternalStore } from "react";

// Same geometry as the drawing canvas and the backend guide spiral.
export const SIZE = 600;
export const CENTER = SIZE / 2;
export const TURNS = 3;
export const MAX_RADIUS = 250;

/** [x, y, t (ms), stroke] in canvas coordinates. */
export type StoredPoint = [number, number, number, number];

export interface StoredDrawing {
  score: number;
  points: StoredPoint[];
  features?: Record<string, number>;
  baseline?: number | null;
  contributions?: Record<string, number> | null;
}

// Kept only in this browser tab (sessionStorage) so the results page can replay the drawing.
// It is never sent anywhere except the analysis request that was already made.
const KEY = "pd.drawing.v1";

export function saveDrawing(d: StoredDrawing) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(d));
  } catch {
    // storage unavailable or full: the replay is simply not shown
  }
}

export function clearDrawing() {
  try {
    sessionStorage.removeItem(KEY);
  } catch {
    // ignore
  }
}

const noopSubscribe = () => () => {};
const readRaw = () => {
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
};

/** The stored drawing, only if it belongs to the drawing score in the page address. */
export function useStoredDrawing(drawingScore: number | undefined): StoredDrawing | null {
  const raw = useSyncExternalStore(noopSubscribe, readRaw, () => null);
  return useMemo(() => {
    if (!raw || drawingScore === undefined) return null;
    try {
      const d = JSON.parse(raw) as StoredDrawing;
      return Math.abs(d.score - drawingScore) < 0.0006 && d.points?.length > 1 ? d : null;
    } catch {
      return null;
    }
  }, [raw, drawingScore]);
}

export function guidePoints(n = 900): { x: number; y: number }[] {
  const maxTheta = TURNS * 2 * Math.PI;
  return Array.from({ length: n + 1 }, (_, i) => {
    const theta = (i / n) * maxTheta;
    const r = (MAX_RADIUS * theta) / maxTheta;
    return { x: CENTER + r * Math.cos(theta), y: CENTER + r * Math.sin(theta) };
  });
}

/** Distance in canvas pixels from each point to the nearest point on the guide spiral. */
export function deviations(points: StoredPoint[]): number[] {
  const guide = guidePoints(1200);
  return points.map(([x, y]) => {
    let best = Infinity;
    for (const g of guide) {
      const d = (g.x - x) ** 2 + (g.y - y) ** 2;
      if (d < best) best = d;
    }
    return Math.sqrt(best);
  });
}
