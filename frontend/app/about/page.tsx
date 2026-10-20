import SiteNav from "@/components/SiteNav";

export default function AboutPage() {
  return (
    <>
      <SiteNav />
      <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-12">
        <h1 className="font-serif text-4xl font-medium tracking-tight">About</h1>

        <h2 className="mt-10 font-serif text-2xl font-medium">What this is</h2>
        <p className="mt-3 text-muted">
          A university research prototype (Creativity, Problem Solving &amp; Innovation project) that
          explores whether voice, spiral drawing and hand-motion signals can support early Parkinson&apos;s
          screening using commonly available devices. It does not diagnose anything.
        </p>

        <h2 className="mt-10 font-serif text-2xl font-medium">How it works</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
          <li>Each signal has its own model, trained on a public dataset, and gives a probability from 0 to 1.</li>
          <li>The combined score is the plain average of the reliable tests you completed (currently drawing, and motion once trained), shown out of 100.</li>
          <li>The three datasets contain different people, so the combination is a prototype and has not been validated.</li>
        </ul>

        <h2 className="mt-10 font-serif text-2xl font-medium">Current status</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
          <li>Drawing: a model exists, trained on 40 people using a stylus and tablet. Mouse and touch drawings are not validated.</li>
          <li>Voice: a model exists, but it is probably telling recording setups apart rather than detecting disease, so by default it is left out of the combined score.</li>
          <li>Motion: no model is trained yet, so that test cannot produce a score.</li>
        </ul>

        <h2 className="mt-10 font-serif text-2xl font-medium">Privacy</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
          <li>Recordings, drawings and motion files are processed in memory and are not saved by the server.</li>
          <li>No name, account or medical record is requested.</li>
          <li>The combined-result page puts only the numeric scores in the web address.</li>
        </ul>

        <h2 className="mt-10 font-serif text-2xl font-medium">Limitations</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-muted marker:text-accent">
          <li>Small training datasets and no clinical validation.</li>
          <li>A high or low score is not a diagnosis. Please see a healthcare professional for any health concern.</li>
        </ul>
      </main>
    </>
  );
}
