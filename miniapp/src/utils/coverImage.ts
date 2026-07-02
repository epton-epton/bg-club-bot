import type { CSSProperties } from "react";

const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

/** API returns paths like /api/v1/.../cover and /uploads/... — prefix with API host in prod. */
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url?.trim()) {
    return null;
  }
  const trimmed = url.trim();
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  if (!trimmed.startsWith("/api/") && !trimmed.startsWith("/uploads/")) {
    return trimmed;
  }
  if (!API_BASE) {
    return trimmed;
  }
  return `${API_BASE}${trimmed}`;
}

export function coverImageStyle(imageUrl: string): CSSProperties {
  const resolved = resolveMediaUrl(imageUrl) ?? imageUrl;
  const safe = resolved.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return { "--cover-image": `url("${safe}")` } as CSSProperties;
}
