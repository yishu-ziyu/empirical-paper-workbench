export const DEFAULT_LOCAL_API_BASE = "http://127.0.0.1:8765";
const LOCAL_API_BASE_STORAGE_KEY = "empiricalWorkbench.apiBase";

declare global {
  interface Window {
    __VITE_API_BASE_URL?: string;
  }
}

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

function configuredApiBase(): string {
  const queryBase = queryApiBase();
  if (queryBase) return queryBase;

  const env = import.meta.env as Record<string, string | undefined>;
  const envBase = env[`VITE_${"API_BASE_URL"}`]?.trim();
  if (envBase) return stripTrailingSlash(envBase);

  const runtimeBase =
    typeof window !== "undefined" ? window.__VITE_API_BASE_URL?.trim() : "";
  if (runtimeBase) return stripTrailingSlash(runtimeBase);

  const storedBase = storedApiBase();
  if (storedBase && isViteLocalFrontend()) return storedBase;

  return "";
}

function queryApiBase(): string {
  if (typeof window === "undefined") return "";
  const params = new URLSearchParams(window.location.search);
  const value = params.get("api_base") ?? params.get("apiBase") ?? "";
  const normalized = stripTrailingSlash(value.trim());
  if (!normalized) return "";

  try {
    window.localStorage.setItem(LOCAL_API_BASE_STORAGE_KEY, normalized);
  } catch {
    // Local browser storage can be unavailable in private or restricted contexts.
  }

  return normalized;
}

function storedApiBase(): string {
  if (typeof window === "undefined") return "";
  try {
    return stripTrailingSlash(window.localStorage.getItem(LOCAL_API_BASE_STORAGE_KEY)?.trim() ?? "");
  } catch {
    return "";
  }
}

function isViteLocalFrontend(): boolean {
  if (typeof window === "undefined") return false;
  const { protocol, hostname, port } = window.location;
  const portNumber = Number(port);
  return (
    protocol === "http:" &&
    (hostname === "127.0.0.1" || hostname === "localhost") &&
    (portNumber === 4173 || (portNumber >= 5170 && portNumber <= 5199))
  );
}

export function apiBase(): string {
  const configured = configuredApiBase();
  if (configured) return configured;
  return isViteLocalFrontend() ? DEFAULT_LOCAL_API_BASE : "";
}

export function setBrowserApiBase(value: string): void {
  if (typeof window === "undefined") return;
  const normalized = stripTrailingSlash(value.trim());
  if (!normalized) return;
  try {
    window.localStorage.setItem(LOCAL_API_BASE_STORAGE_KEY, normalized);
  } catch {
    // Local browser storage can be unavailable in private or restricted contexts.
  }
}

export function apiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${apiBase()}${normalizedPath}`;
}
