const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public kind: "unreachable" | "server",
  ) {
    super(message);
  }
}

async function request<T>(path: string, timeoutMs = 5000): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_URL}${path}`, {
      signal: controller.signal,
      cache: "no-store",
    });
    if (!res.ok) {
      throw new ApiError(`The server responded with status ${res.status}.`, "server");
    }
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError("Could not reach the backend.", "unreachable");
  } finally {
    clearTimeout(timer);
  }
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export const getHealth = () => request<HealthResponse>("/api/health");
