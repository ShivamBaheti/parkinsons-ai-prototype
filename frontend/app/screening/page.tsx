import ScreeningFlow from "@/components/ScreeningFlow";
import SiteNav from "@/components/SiteNav";

export default function ScreeningPage() {
  return (
    <>
    <SiteNav />
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
      <h1 className="mt-4 font-serif text-4xl font-medium tracking-tight">Screening</h1>

      <ScreeningFlow />
    </main>
    </>
  );
}
