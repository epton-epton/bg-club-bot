import type { BggSearchItem, Game } from "../types/api";

function normalizeTitle(title: string) {
  return title.toLowerCase().replace(/[^a-z0-9а-яёіїєґ]/gi, "");
}

export type BggCatalogMatch =
  | { kind: "update"; game: Game }
  | { kind: "link"; game: Game }
  | { kind: "new" };

export function isBggMetadataIncomplete(game: Game): boolean {
  if (!game.bgg_id) {
    return false;
  }
  const hasPlayers = game.players_min != null || game.players_max != null;
  return !hasPlayers || game.duration_minutes == null || game.bgg_rating == null;
}

export function findBggCatalogMatch(games: Game[], item: BggSearchItem): BggCatalogMatch {
  const byBgg = games.find((game) => game.bgg_id === item.bgg_id);
  if (byBgg) {
    return { kind: "update", game: byBgg };
  }

  const normalized = normalizeTitle(item.title);
  const byTitle = games.find(
    (game) => game.bgg_id == null && game.is_active && normalizeTitle(game.title) === normalized,
  );
  if (byTitle) {
    return { kind: "link", game: byTitle };
  }

  return { kind: "new" };
}
