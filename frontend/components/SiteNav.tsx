"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/screening", label: "Screening" },
  { href: "/about", label: "About" },
];

export default function SiteNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Main" className="sticky top-0 z-10 border-b border-line bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-2xl items-center justify-between px-6 py-3">
        <Link href="/" className="font-serif text-lg font-medium text-ink">
          Parkinson&apos;s Screening
        </Link>
        <ul className="flex gap-1 text-sm">
          {LINKS.map((l) => {
            const active = l.href === "/" ? pathname === "/" : pathname.startsWith(l.href);
            return (
              <li key={l.href}>
                <Link
                  href={l.href}
                  aria-current={active ? "page" : undefined}
                  className={`rounded-full px-3.5 py-1.5 font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent ${
                    active ? "bg-accent text-accent-ink" : "text-muted hover:bg-line/60 hover:text-ink"
                  }`}
                >
                  {l.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}
