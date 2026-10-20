const NAMES: Record<string, { label: string; describe: (v: number) => string }> = {
  radial_residual_rms: {
    label: "Spiral regularity",
    describe: (v) => `Your line drifted about ${(v * 100).toFixed(1)}% of the spiral's radius away from a smooth outward curve.`,
  },
  speed_cv: {
    label: "Speed steadiness",
    describe: (v) => `Your speed varied by about ${(v * 100).toFixed(0)}% around its average.`,
  },
  pause_fraction: {
    label: "Pauses",
    describe: (v) => `You were nearly still for ${(v * 100).toFixed(0)}% of the drawing.`,
  },
  heading_change_std: {
    label: "Direction smoothness",
    describe: (v) => `Your direction typically shifted by ${((v * 180) / Math.PI).toFixed(1)}° between samples.`,
  },
  speed_std: { label: "Speed spread", describe: (v) => `Speed spread of ${v.toFixed(2)} spiral radii per second.` },
  speed_mean: { label: "Average speed", describe: (v) => `You drew at about ${v.toFixed(2)} spiral radii per second.` },
  jerk_rms: { label: "Movement smoothness", describe: (v) => `Sudden changes in acceleration measured ${v.toFixed(1)}.` },
  accel_rms: { label: "Acceleration", describe: (v) => `Acceleration measured ${v.toFixed(2)}.` },
  tremor_band_ratio: {
    label: "Fast wobble",
    describe: (v) => `${(v * 100).toFixed(0)}% of your speed variation was in the 4–8 Hz range.`,
  },
  tremor_peak_hz: { label: "Main wobble rate", describe: (v) => `The strongest rhythm in your movement was ${v.toFixed(1)} Hz.` },
};

export default function WhyScore({
  contributions,
  baseline,
  features,
  score,
}: {
  contributions: Record<string, number>;
  baseline: number | null | undefined;
  features: Record<string, number>;
  score: number;
}) {
  const rows = Object.entries(contributions)
    .filter(([k, c]) => Math.abs(c) >= 0.5 && NAMES[k] && features[k] !== undefined)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 4);
  if (rows.length === 0) return null;
  const max = Math.max(...rows.map(([, c]) => Math.abs(c)));

  return (
    <section className="mt-10" aria-labelledby="why-heading">
      <h2 id="why-heading" className="font-serif text-2xl font-medium">
        Why this score
      </h2>
      <p className="mt-2 text-muted">
        {baseline != null && (
          <>
            The model starts at <strong className="text-ink">{Math.round(baseline)}</strong> and your drawing moved it
            to <strong className="text-ink">{score}</strong>.{" "}
          </>
        )}
        These are the measurements that moved it most.
      </p>

      <ul className="mt-5 space-y-5">
        {rows.map(([k, c]) => {
          const up = c > 0;
          const width = (Math.abs(c) / max) * 50;
          return (
            <li key={k}>
              <div className="flex flex-wrap items-baseline justify-between gap-x-4">
                <span className="font-semibold">{NAMES[k].label}</span>
                <span className="text-sm font-semibold" style={{ color: up ? "#a23624" : "#17704a" }}>
                  {up ? "Raised" : "Lowered"} the score by {Math.abs(c).toFixed(1)}
                </span>
              </div>
              <div className="relative mt-2 h-2.5 rounded-full bg-line" role="img" aria-label={`${up ? "Raised" : "Lowered"} the score by ${Math.abs(c).toFixed(1)} points`}>
                <span className="absolute left-1/2 top-[-3px] h-[16px] w-px bg-ink/30" aria-hidden="true" />
                <span
                  className="absolute top-0 h-2.5 rounded-full"
                  style={{
                    width: `${width}%`,
                    background: up ? "#c4432f" : "#1f8a5b",
                    ...(up ? { left: "50%" } : { right: "50%" }),
                  }}
                />
              </div>
              <p className="mt-1.5 text-sm text-muted">{NAMES[k].describe(features[k])}</p>
            </li>
          );
        })}
      </ul>
      <p className="mt-4 text-sm text-muted">
        This shows how the model weighed your measurements, not a clinical explanation. It was trained on stylus
        drawings, so mouse or touch drawings may be weighed differently.
      </p>
    </section>
  );
}
