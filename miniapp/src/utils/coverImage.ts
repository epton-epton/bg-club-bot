import type { CSSProperties } from "react";

const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

function isApiMediaPath(url: string): boolean {
  return url.startsWith("/api/") || url.startsWith("/uploads/");
}

/** Prefer direct CDN URLs; API paths stay same-origin (nginx proxy in prod, Vite in dev). */
export function gameCoverSrc(game: {
  image_url: string | null;
  cover_url: string | null;
}): string | null {
  const image = game.image_url?.trim();
  if (image && /^https?:\/\//i.test(image)) {
    return image;
  }
  return resolveMediaUrl(game.cover_url);
}

export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url?.trim()) {
    return null;
  }
  const trimmed = url.trim();
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  if (isApiMediaPath(trimmed)) {
    // Same-origin: miniapp nginx or Vite dev proxy
    if (!API_BASE) {
      return trimmed;
    }
    return `${API_BASE}${trimmed}`;
  }
  return trimmed;
}

export function coverImageStyle(imageUrl: string): CSSProperties {
  const resolved = resolveMediaUrl(imageUrl) ?? imageUrl;
  const safe = resolved.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return { "--cover-image": `url("${safe}")` } as CSSProperties;
}
