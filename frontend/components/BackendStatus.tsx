"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

type State = "checking" | "online" | "offline";

export default function BackendStatus() {
  const [state, setState] = useState<State>("checking");

  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const health = await getHealth();
        if (!cancelled) setState(health.status === "ok" ? "online" : "offline");
      } catch {
        if (!cancelled) setState("offline");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const retry = () => {
    setState("checking");
    setAttempt((n) => n + 1);
  };

  const dot =
    state === "online" ? "bg-emerald-600" : state === "offline" ? "bg-red-600" : "bg-muted";
  const label =
    state === "online"
      ? "Backend connected"
      : state === "offline"
        ? "Backend not reachable"
        : "Checking backend";

  return (
    <div className="flex items-center gap-2 text-sm text-muted" role="status" aria-live="polite">
      <span className={`h-2 w-2 rounded-full ${dot}`} aria-hidden="true" />
      <span>{label}</span>
      {state === "offline" && (
        <button
          onClick={retry}
          className="rounded text-accent underline underline-offset-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Retry
        </button>
      )}
    </div>
  );
}
