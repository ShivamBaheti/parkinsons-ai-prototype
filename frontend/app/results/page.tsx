import ResultsView from "@/components/ResultsView";
import SiteNav from "@/components/SiteNav";

function parseScore(value: string | string[] | undefined): number | undefined {
  if (typeof value !== "string") return undefined;
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 && n <= 1 ? n : undefined;
}

export default async function ResultsPage(props: PageProps<"/results">) {
  const params = await props.searchParams;
  const scores = {
    voice: parseScore(params.voice),
    drawing: parseScore(params.drawing),
    motion: parseScore(params.motion),
  };

  return (
    <>
      <SiteNav />
      <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
        <h1 className="font-serif text-4xl font-medium tracking-tight">Screening results</h1>
        <ResultsView scores={scores} />
      </main>
    </>
  );
}
