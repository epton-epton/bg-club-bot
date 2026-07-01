import type { CSSProperties } from "react";

export function coverImageStyle(imageUrl: string): CSSProperties {
  const safe = imageUrl.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return { "--cover-image": `url("${safe}")` } as CSSProperties;
}
