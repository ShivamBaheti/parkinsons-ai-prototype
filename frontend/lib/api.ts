const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = 5000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal, cache: "no-store" });
  } catch {
    throw new ApiError(
      "Could not reach the backend. Check that it is running on port 8000.",
      "unreachable",
    );
  } finally {
    clearTimeout(timer);
  }

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    // non-JSON response; handled below
  }
  if (!res.ok) {
    const err = body as { error?: string; message?: string } | null;
    throw new ApiError(
      err?.message ?? `The server responded with status ${res.status}.`,
      err?.error ?? "server_error",
    );
  }
  return body as T;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export const getHealth = () => request<HealthResponse>("/api/health");

export interface ModalityResult {
  modality: string;
  score: number;
  label: string;
  note?: string;
  reliable?: boolean;
}

export function analyzeVoice(wav: Blob) {
  const form = new FormData();
  form.append("file", wav, "recording.wav");
  return request<ModalityResult>("/api/voice/analyze", { method: "POST", body: form }, 30000);
}

export interface DrawingPoint {
  x: number;
  y: number;
  t: number; // milliseconds since the first point
  stroke: number;
  pressure?: number;
}

export function analyzeDrawing(points: DrawingPoint[], canvasSize: number, inputType?: string) {
  return request<ModalityResult>(
    "/api/drawing/analyze",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ points, canvas_size: canvasSize, input_type: inputType }),
    },
    15000,
  );
}

export function analyzeMotion(file: File) {
  const form = new FormData();
  form.append("file", file, file.name);
  return request<ModalityResult>("/api/motion/analyze", { method: "POST", body: form }, 30000);
}

export interface ScreeningResponse {
  screening_score: number; // 0-100
  modalities: { voice: number | null; drawing: number | null; motion: number | null };
  interpretation: "elevated_screening_signal" | "lower_screening_signal";
  fusion: {
    method: string;
    validated: boolean;
    threshold: number;
    modalities_used: string[];
    modalities_missing: string[];
    modalities_excluded: string[];
    contributions: Record<string, number>;
    note: string;
  };
  disclaimer: string;
}

export function analyzeScreening(scores: { voice?: number; drawing?: number; motion?: number }) {
  return request<ScreeningResponse>("/api/screening/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scores),
  });
}

export interface ModelInfoResponse {
  modalities: Record<string, { available: boolean; metadata: Record<string, unknown> | null }>;
  fusion: { method: string; validated: boolean; threshold: number; description: string };
}

export const getModelInfo = () => request<ModelInfoResponse>("/api/model-info");
