import Link from "next/link";
import BackendStatus from "@/components/BackendStatus";
import SpiralMark from "@/components/SpiralMark";
import { BANDS } from "@/lib/risk";

export default function Home() {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-6 sm:px-10">
      <header className="flex items-center justify-between border-b border-line pb-4">
        <span className="font-serif text-lg font-medium">Parkinson&apos;s Screening</span>
        <nav aria-label="Main" className="flex items-center gap-2 text-sm">
          <Link href="/screening" className="rounded-full px-3.5 py-1.5 font-medium text-muted hover:bg-line/60 hover:text-ink">
            Screening
          </Link>
          <Link href="/about" className="rounded-full px-3.5 py-1.5 font-medium text-muted hover:bg-line/60 hover:text-ink">
            About
          </Link>
          <BackendStatus />
        </nav>
      </header>

      <main className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:py-20">
        <div>
          <h1 className="font-serif text-5xl font-medium leading-[1.05] tracking-tight sm:text-7xl">
            Draw a spiral.
            <br />
            See your signal.
          </h1>
          <p className="mt-6 max-w-xl text-xl text-muted">
            An AI research prototype that looks at how you draw, speak and move, and turns it into a Low, Medium or
            High screening signal.
          </p>

          <ul className="mt-6 list-disc space-y-1 pl-5 text-muted marker:text-accent">
            <li>Voice recordings</li>
            <li>Touchscreen spiral drawing, replayed line by line</li>
            <li>Smartphone and wearable motion data</li>
          </ul>

          <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-4">
            <Link
              href="/screening"
              className="inline-block rounded-full bg-accent px-8 py-3.5 font-semibold text-accent-ink shadow-lg shadow-accent/30 transition-colors hover:bg-[#0a5560] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
            >
              Start screening
            </Link>
            <ul className="flex flex-wrap gap-2" aria-label="Possible results">
              {BANDS.map((b) => (
                <li
                  key={b.key}
                  className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold"
                  style={{ background: b.tint, color: b.ink }}
                >
                  <span className="h-2 w-2 rounded-full" style={{ background: b.color }} aria-hidden="true" />
                  {b.label}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="flex justify-center lg:justify-end">
          <div className="w-full max-w-md rounded-full bg-white/70 p-6 shadow-[0_30px_80px_-25px_rgba(14,107,120,0.45)] ring-1 ring-line">
            <SpiralMark />
          </div>
        </div>
      </main>
    </div>
  );
}
