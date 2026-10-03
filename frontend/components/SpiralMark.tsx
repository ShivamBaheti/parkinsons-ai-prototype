/**
 * A hand-drawn-looking Archimedean spiral: the test this app is built around.
 * Wobble grows with radius, like an unsteady line. Deterministic (no randomness),
 * so server and client render identical markup.
 */
function spiralPath(): string {
  const cx = 200;
  const cy = 200;
  const turns = 4;
  const steps = 420;
  const maxTheta = turns * 2 * Math.PI;
  const points: string[] = [];
  for (let i = 0; i <= steps; i++) {
    const theta = (i / steps) * maxTheta;
    const base = 8 + (theta / maxTheta) * 170;
    const wobble = Math.sin(theta * 7.3) * (0.4 + (theta / maxTheta) * 2.2);
    const r = base + wobble;
    const x = cx + r * Math.cos(theta);
    const y = cy + r * Math.sin(theta);
    points.push(`${i === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`);
  }
  return points.join(" ");
}

export default function SpiralMark() {
  return (
    <svg
      viewBox="0 0 400 400"
      role="img"
      aria-label="A hand-drawn spiral, the kind of drawing used in movement screening"
      className="h-auto w-full max-w-md"
    >
      <path
        d={spiralPath()}
        pathLength={1}
        className="spiral-path"
        fill="none"
        stroke="var(--accent)"
        strokeWidth={3}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
