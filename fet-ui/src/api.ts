const API_URL = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function messageFromBody(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object" || !("detail" in body)) {
    return fallback;
  }
  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return String(item);
      })
      .join(", ");
  }
  return fallback;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = localStorage.getItem("token");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (response.status === 401 && !path.startsWith("/api/auth/")) {
    localStorage.removeItem("token");
    if (!window.location.pathname.startsWith("/login")) {
      window.location.assign("/login");
    }
  }
  if (!response.ok) {
    let message = response.statusText || "Request failed";
    try {
      message = messageFromBody(await response.json(), message);
    } catch {
      // The response had no JSON body.
    }
    throw new ApiError(response.status, message);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}
