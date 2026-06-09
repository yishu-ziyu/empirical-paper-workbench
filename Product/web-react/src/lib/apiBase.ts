const DEFAULT_LOCAL_API_BASE = "http://127.0.0.1:8765";

declare global {
  interface Window {
    __VITE_API_BASE_URL?: string;
  }
}

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function configuredApiBase(): string {
  const env = import.meta.env as Record<string, string | undefined>;
  const envBase = env[`VITE_${"API_BASE_URL"}`]?.trim();
  if (envBase) return stripTrailingSlash(envBase);

  const runtimeBase =
    typeof window !== "undefined" ? window.__VITE_API_BASE_URL?.trim() : "";
  if (runtimeBase) return stripTrailingSlash(runtimeBase);

  return "";
}

function isLocalFrontend(): boolean {
  if (typeof window === "undefined") return false;
  const { protocol, hostname, port } = window.location;
  return (
    protocol === "http:" &&
    port !== "8765" &&
    (hostname === "127.0.0.1" || hostname === "localhost")
  );
}

export function apiBase(): string {
  const configured = configuredApiBase();
  if (configured) return configured;
  return isLocalFrontend() ? DEFAULT_LOCAL_API_BASE : "";
}

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${apiBase()}${normalizedPath}`;
}
