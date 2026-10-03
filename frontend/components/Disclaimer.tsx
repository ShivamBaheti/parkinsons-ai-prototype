export default function Disclaimer({ variant = "short" }: { variant?: "short" | "full" }) {
  if (variant === "short") {
    return (
      <p
        role="note"
        className="border-l-4 border-notice-line bg-notice-bg px-4 py-3 text-sm text-notice-ink"
      >
        ⚠️ This tool is a research screening prototype and is not a medical diagnosis.
      </p>
    );
  }
  return (
    <div
      role="note"
      className="border-l-4 border-notice-line bg-notice-bg px-4 py-3 text-sm text-notice-ink"
    >
      <p className="font-semibold">Research Prototype — Not a Medical Diagnosis</p>
      <p className="mt-1">
        This application is an experimental AI-based screening system intended for academic
        research and demonstration. Its outputs should not be interpreted as a diagnosis of
        Parkinson&apos;s Disease or used to make medical decisions. Consult a qualified
        healthcare professional for clinical evaluation.
      </p>
    </div>
  );
}
