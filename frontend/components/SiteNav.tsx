import Link from "next/link";

export default function SiteNav() {
  return (
    <nav aria-label="Main" className="border-b border-line">
      <ul className="mx-auto flex max-w-2xl gap-6 px-6 py-3 text-sm">
        <li><Link href="/" className="text-accent underline underline-offset-2">Home</Link></li>
        <li><Link href="/screening" className="text-accent underline underline-offset-2">Screening</Link></li>
        <li><Link href="/about" className="text-accent underline underline-offset-2">About</Link></li>
      </ul>
    </nav>
  );
}
