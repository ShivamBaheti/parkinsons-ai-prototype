import Link from "next/link";
import Disclaimer from "@/components/Disclaimer";

export default function ScreeningPage() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-16">
      <h1 className="font-serif text-4xl font-medium tracking-tight">Screening</h1>
      <p className="mt-4 text-muted">
        The screening tests are not built yet. The voice test arrives in Phase 2, drawing in
        Phase 3, and motion in Phase 4.
      </p>
      <div className="mt-8">
        <Disclaimer variant="full" />
      </div>
      <Link href="/" className="mt-8 inline-block text-accent underline underline-offset-2">
        Back to home
      </Link>
    </main>
  );
}
