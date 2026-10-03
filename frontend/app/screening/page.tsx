import Link from "next/link";
import Disclaimer from "@/components/Disclaimer";
import DrawingCanvas from "@/components/DrawingCanvas";
import VoiceRecorder from "@/components/VoiceRecorder";

export default function ScreeningPage() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
      <Link href="/" className="text-sm text-accent underline underline-offset-2">
        Back to home
      </Link>
      <h1 className="mt-4 font-serif text-4xl font-medium tracking-tight">Screening</h1>
      <div className="mt-6">
        <Disclaimer variant="full" />
      </div>

      <section className="mt-10">
        <h2 className="font-serif text-2xl font-medium">Step 1 — Voice</h2>
        <div className="mt-4">
          <VoiceRecorder />
        </div>
      </section>

      <section className="mt-12 border-t border-line pt-8">
        <h2 className="font-serif text-2xl font-medium">Step 2 — Drawing</h2>
        <div className="mt-4">
          <DrawingCanvas />
        </div>
      </section>

      <section className="mt-12 border-t border-line pt-6 text-muted">
        <h2 className="font-semibold text-ink">Step 3 — Motion</h2>
        <p className="mt-1 text-sm">Not built yet.</p>
      </section>
    </main>
  );
}
