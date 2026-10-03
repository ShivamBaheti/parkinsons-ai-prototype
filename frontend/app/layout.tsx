import type { Metadata } from "next";
import "@fontsource-variable/figtree";
import "@fontsource-variable/newsreader";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI-Assisted Parkinson's Screening",
  description:
    "A research prototype exploring AI analysis of voice, drawing and movement patterns. Not a medical diagnosis.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
