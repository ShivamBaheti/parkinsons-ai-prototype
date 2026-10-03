import Link from "next/link";
import BackendStatus from "@/components/BackendStatus";
import Disclaimer from "@/components/Disclaimer";
import SpiralMark from "@/components/SpiralMark";

export default function Home() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-6 sm:px-10">
      <header className="flex items-center justify-between border-b border-line pb-4">
        <span className="font-semibold">Parkinson&apos;s Screening Prototype</span>
        <BackendStatus />
      </header>

      <main className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:py-20">
        <div>
          <h1 className="font-serif text-4xl font-medium leading-tight tracking-tight sm:text-6xl">
            AI-Assisted Parkinson&apos;s Screening
          </h1>
          <p className="mt-5 text-xl text-muted">
            Explore AI-based analysis of voice, drawing and movement patterns.
          </p>
          <p className="mt-5 max-w-xl leading-relaxed text-muted">
            This research prototype explores whether signals that can be collected using commonly
            available devices can assist with early Parkinson&apos;s risk screening.
          </p>

          <ul className="mt-6 list-disc space-y-1 pl-5 text-muted marker:text-accent">
            <li>Voice recordings</li>
            <li>Touchscreen spiral and wave drawing</li>
            <li>Smartphone and wearable motion data</li>
          </ul>

          <Link
            href="/screening"
            className="mt-8 inline-block rounded-md bg-accent px-7 py-3 font-semibold text-accent-ink transition-colors hover:bg-[#0a5560] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Start Screening
          </Link>

          <div className="mt-8 max-w-xl">
            <Disclaimer />
          </div>
        </div>

        <div className="flex justify-center lg:justify-end">
          <SpiralMark />
        </div>
      </main>
    </div>
  );
}
