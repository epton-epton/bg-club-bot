import { useCallback, useEffect, useState } from "react";

import { api } from "../api/client";
import { Chip } from "../components/Chip";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useMe } from "../hooks/useMe";
import type { BggSearchItem, Game } from "../types/api";
import { findBggCatalogMatch, isBggMetadataIncomplete } from "../utils/bggCatalog";
import { gameCoverSrc } from "../utils/coverImage";
import { formatPlayers } from "../utils/format";

export function GamesPage() {
  const { t } = useAppSettings();
  const { isAdmin } = useMe();
  const [reloadKey, setReloadKey] = useState(0);
  const [showAdmin, setShowAdmin] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionInfo, setActionInfo] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const fetchGames = useCallback(
    () => (isAdmin ? api.adminGetGames() : api.getGames()),
    [isAdmin],
  );

  const { data, loading, error } = useAsyncData(fetchGames, [reloadKey, isAdmin]);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  async function runAction(id: number, action: () => Promise<unknown>) {
    setActionError(null);
    setActionInfo(null);
    setBusyId(id);
    try {
      await action();
      refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setBusyId(null);
    }
  }

  async function runBggUpdate(game: Game) {
    if (!game.bgg_id) return;
    setActionError(null);
    setActionInfo(null);
    setBusyId(game.id);
    try {
      await api.bggImport(game.bgg_id);
      setActionInfo(t("games.bggUpdated", { title: game.title }));
      refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("games.bggSyncError"));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  const games = data ?? [];
  const activeGames = games.filter((g) => g.is_active);

  return (
    <section className="page">
      <header className="page-header page-header--row">
        <div>
          <h1>{t("games.title")}</h1>
          <p className="page-subtitle">{t("games.subtitle", { n: activeGames.length })}</p>
        </div>
        {isAdmin ? (
          <button
            type="button"
            className="btn btn--primary btn--compact"
            onClick={() => setShowAdmin((v) => !v)}
          >
            {showAdmin ? t("games.hideAdmin") : t("games.manage")}
          </button>
        ) : null}
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}
      {actionInfo ? <p className="form-hint form-hint--success">{actionInfo}</p> : null}

      {isAdmin && showAdmin ? (
        <GamesAdminPanel
          games={games}
          onRefresh={refresh}
          onError={setActionError}
          onInfo={(message) => {
            setActionError(null);
            setActionInfo(message);
          }}
        />
      ) : null}

      {!games.length ? (
        <p className="empty-hint">{t("games.empty")}</p>
      ) : (
        <ul className="card-list">
          {(isAdmin ? games : activeGames).map((game) => (
            <GameCard
              key={game.id}
              game={game}
              isAdmin={isAdmin}
              busy={busyId === game.id}
              onDeactivate={() => runAction(game.id, () => api.deactivateGame(game.id))}
              onReactivate={() =>
                runAction(game.id, () => api.updateGame(game.id, { is_active: true }))
              }
              onSave={(payload) => runAction(game.id, () => api.updateGame(game.id, payload))}
              onBggUpdate={game.bgg_id ? () => runBggUpdate(game) : undefined}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

interface GamesAdminPanelProps {
  games: Game[];
  onRefresh: () => void;
  onError: (message: string | null) => void;
  onInfo: (message: string | null) => void;
}

function GamesAdminPanel({ games, onRefresh, onError, onInfo }: GamesAdminPanelProps) {
  const { t } = useAppSettings();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [playersMin, setPlayersMin] = useState("");
  const [playersMax, setPlayersMax] = useState("");
  const [duration, setDuration] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [manualOpen, setManualOpen] = useState(false);
  const [bggOpen, setBggOpen] = useState(false);
  const [bggQuery, setBggQuery] = useState("");
  const debouncedBggQuery = useDebouncedValue(bggQuery, 400);
  const [bggResults, setBggResults] = useState<BggSearchItem[]>([]);
  const [bggSearching, setBggSearching] = useState(false);
  const [bggImporting, setBggImporting] = useState<number | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!bggOpen) {
      return;
    }

    const query = debouncedBggQuery.trim();
    if (query.length < 2) {
      setBggResults([]);
      setBggSearching(false);
      return;
    }

    let cancelled = false;
    setBggSearching(true);
    onError(null);

    void api
      .bggSearch(query)
      .then((results) => {
        if (!cancelled) setBggResults(results);
      })
      .catch((err) => {
        if (!cancelled) {
          onError(err instanceof Error ? err.message : t("games.bggSearchError"));
        }
      })
      .finally(() => {
        if (!cancelled) setBggSearching(false);
      });

    return () => {
      cancelled = true;
    };
  }, [bggOpen, debouncedBggQuery, onError, t]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    onError(null);
    try {
      await api.createGame({
        title: title.trim(),
        description: description.trim() || null,
        players_min: playersMin ? Number(playersMin) : null,
        players_max: playersMax ? Number(playersMax) : null,
        duration_minutes: duration ? Number(duration) : null,
      });
      setTitle("");
      setDescription("");
      setPlayersMin("");
      setPlayersMax("");
      setDuration("");
      setManualOpen(false);
      onRefresh();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("games.createError"));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleBggImport(bggId: number, linkGameId?: number) {
    setBggImporting(bggId);
    onError(null);
    try {
      const game = await api.bggImport(bggId, linkGameId);
      setBggResults([]);
      setBggQuery("");
      onRefresh();
      onInfo(
        linkGameId
          ? t("games.bggLinked", { title: game.title })
          : t("games.bggImported", { title: game.title }),
      );
    } catch (err) {
      onError(err instanceof Error ? err.message : t("games.bggImportError"));
    } finally {
      setBggImporting(null);
    }
  }

  async function handleBggSync() {
    setSyncing(true);
    setSyncMessage(null);
    onError(null);
    onInfo(null);
    try {
      const result = await api.bggSyncAll();
      onRefresh();
      const message =
        result.failed > 0
          ? t("games.bggSyncPartial", { synced: result.synced, failed: result.failed })
          : result.synced > 0
            ? t("games.bggSyncDone", { synced: result.synced })
            : t("games.bggSyncNone");
      setSyncMessage(message);
      onInfo(message);
    } catch (err) {
      onError(err instanceof Error ? err.message : t("games.bggSyncError"));
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div className="admin-games">
      <h2 className="admin-games__heading">{t("games.adminTitle")}</h2>

      <div className="panel form-panel admin-games-panel">
        <section className="admin-games-panel__section">
          <details
            className="admin-games-panel__expand"
            open={manualOpen}
            onToggle={(event) => setManualOpen(event.currentTarget.open)}
          >
            <summary className="admin-games-panel__section-title admin-games-panel__section-summary">
              {t("games.addManual")}
            </summary>
            <div className="admin-games-panel__expand-body">
              <form className="admin-games-panel__manual-form" onSubmit={handleCreate}>
            <label className="form-field">
              <span className="form-label">{t("games.manualTitle")}</span>
              <input
                className="form-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </label>
            <label className="form-field">
              <span className="form-label">{t("games.description")}</span>
              <textarea
                className="form-input form-input--textarea"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </label>
            <div className="form-row">
              <label className="form-field">
                <span className="form-label">{t("games.playersMin")}</span>
                <input
                  className="form-input"
                  type="number"
                  min={1}
                  value={playersMin}
                  onChange={(e) => setPlayersMin(e.target.value)}
                />
              </label>
              <label className="form-field">
                <span className="form-label">{t("games.playersMax")}</span>
                <input
                  className="form-input"
                  type="number"
                  min={1}
                  value={playersMax}
                  onChange={(e) => setPlayersMax(e.target.value)}
                />
              </label>
            </div>
            <label className="form-field">
              <span className="form-label">{t("games.duration")}</span>
              <input
                className="form-input"
                type="number"
                min={1}
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </label>
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              {submitting ? t("games.saving") : t("games.addGame")}
            </button>
              </form>
            </div>
          </details>
        </section>

        <section className="admin-games-panel__section admin-games-panel__section--bgg">
          <details
            className="admin-games-panel__expand"
            open={bggOpen}
            onToggle={(event) => setBggOpen(event.currentTarget.open)}
          >
            <summary className="admin-games-panel__section-title admin-games-panel__section-summary">
              {t("games.addFromBgg")}
            </summary>
            <div className="admin-games-panel__expand-body">
              <div className="form-field admin-games-panel__search">
                <input
                  className="form-input"
                  value={bggQuery}
                  onChange={(e) => setBggQuery(e.target.value)}
                  placeholder={t("games.bggSearchPlaceholder")}
                  autoComplete="off"
                />
                <p className="form-hint">
                  {bggSearching
                    ? t("games.searching")
                    : bggQuery.trim().length < 2
                      ? t("games.bggSearchMin")
                      : bggResults.length === 0
                        ? t("games.bggSearchEmpty")
                        : t("games.bggSearchHint")}
                </p>
              </div>

              {bggResults.length ? (
                <ul className="row-list">
                  {bggResults.map((item) => {
                    const match = findBggCatalogMatch(games, item);
                    const actionLabel =
                      match.kind === "link"
                        ? t("games.bggLink")
                        : match.kind === "update"
                          ? t("games.bggUpdate")
                          : t("games.import");

                    return (
                      <li key={item.bgg_id} className="row-item row-item--compact">
                        <div className="row-item__body">
                          <strong>{item.title}</strong>
                          {item.year ? <span className="row-item__meta">{item.year}</span> : null}
                          {match.kind === "link" ? (
                            <span className="row-item__meta">
                              {t("games.bggCatalogMatch", { title: match.game.title })}
                            </span>
                          ) : null}
                        </div>
                        <button
                          type="button"
                          className="btn btn--primary btn--compact"
                          disabled={bggImporting === item.bgg_id}
                          onClick={() =>
                            handleBggImport(
                              item.bgg_id,
                              match.kind === "link" ? match.game.id : undefined,
                            )
                          }
                        >
                          {bggImporting === item.bgg_id ? t("games.importing") : actionLabel}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              ) : null}

              <div className="admin-games-panel__sync">
                {syncing ? <p className="form-hint">{t("games.syncingHint")}</p> : null}
                {syncMessage ? <p className="form-hint form-hint--success">{syncMessage}</p> : null}
                <button
                  type="button"
                  className="btn btn--ghost admin-games-panel__sync-btn"
                  disabled={syncing}
                  onClick={handleBggSync}
                >
                  {syncing ? t("games.syncing") : t("games.syncBgg")}
                </button>
                <p className="form-hint admin-games-panel__sync-hint">{t("games.syncBggHint")}</p>
              </div>
            </div>
          </details>
        </section>
      </div>
    </div>
  );
}

interface GameCardProps {
  game: Game;
  isAdmin: boolean;
  busy: boolean;
  onDeactivate: () => void;
  onReactivate: () => void;
  onSave: (payload: {
    title: string;
    description: string | null;
    players_min: number | null;
    players_max: number | null;
    duration_minutes: number | null;
  }) => void;
  onBggUpdate?: () => void;
}

function GameCard({
  game,
  isAdmin,
  busy,
  onDeactivate,
  onReactivate,
  onSave,
  onBggUpdate,
}: GameCardProps) {
  const { t } = useAppSettings();
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(game.title);
  const [description, setDescription] = useState(game.description ?? "");
  const [playersMin, setPlayersMin] = useState(game.players_min?.toString() ?? "");
  const [playersMax, setPlayersMax] = useState(game.players_max?.toString() ?? "");
  const [duration, setDuration] = useState(game.duration_minutes?.toString() ?? "");

  const bggIncomplete = isBggMetadataIncomplete(game);
  const coverSrc = gameCoverSrc(game);

  function handleSave(event: React.FormEvent) {
    event.preventDefault();
    onSave({
      title: title.trim(),
      description: description.trim() || null,
      players_min: playersMin ? Number(playersMin) : null,
      players_max: playersMax ? Number(playersMax) : null,
      duration_minutes: duration ? Number(duration) : null,
    });
    setEditing(false);
  }

  return (
    <li className={`card game-card game-card--rich${!game.is_active ? " game-card--inactive" : ""}`}>
      {coverSrc ? (
        <img className="game-card__thumb" src={coverSrc} alt={game.title} />
      ) : (
        <div className="game-card__thumb game-card__thumb--placeholder">🎲</div>
      )}
      <div className="game-card__content">
        {editing ? (
          <form className="game-card__edit" onSubmit={handleSave}>
            <input
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <textarea
              className="form-input form-input--textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
            />
            <div className="form-row">
              <input
                className="form-input"
                type="number"
                min={1}
                placeholder={t("games.playersMin")}
                value={playersMin}
                onChange={(e) => setPlayersMin(e.target.value)}
              />
              <input
                className="form-input"
                type="number"
                min={1}
                placeholder={t("games.playersMax")}
                value={playersMax}
                onChange={(e) => setPlayersMax(e.target.value)}
              />
            </div>
            <input
              className="form-input"
              type="number"
              min={1}
              placeholder={t("games.duration")}
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
            <div className="session-card__actions">
              <button type="submit" className="btn btn--primary btn--compact" disabled={busy}>
                {t("common.save")}
              </button>
              <button
                type="button"
                className="btn btn--ghost btn--compact"
                onClick={() => setEditing(false)}
              >
                {t("common.cancel")}
              </button>
            </div>
          </form>
        ) : (
          <>
            <div className="row-item__top">
              <h2>{game.title}</h2>
              {!game.is_active ? <Chip tone="pink">{t("games.inactive")}</Chip> : null}
              {game.bgg_rank ? <Chip tone="cyan">{`🏆 #${game.bgg_rank}`}</Chip> : null}
            </div>
            <div className="chip-row game-card__meta">
              {game.bgg_rating ? (
                <Chip tone="muted">{`⭐ ${game.bgg_rating.toFixed(1)}`}</Chip>
              ) : null}
              {game.players_min !== null || game.players_max !== null ? (
                <Chip>{`👥 ${formatPlayers(game.players_min, game.players_max, t)}`}</Chip>
              ) : null}
              {game.duration_minutes ? (
                <Chip>{`⏱ ${t("games.minutes", { n: game.duration_minutes })}`}</Chip>
              ) : null}
              {game.year_published ? <Chip>{`📅 ${game.year_published}`}</Chip> : null}
            </div>
            {game.description ? <p className="game-card__desc">{game.description}</p> : null}
            {isAdmin && bggIncomplete ? (
              <p className="form-hint game-card__bgg-hint">{t("games.bggIncompleteHint")}</p>
            ) : null}
            {isAdmin ? (
              <div className="session-card__actions">
                {onBggUpdate ? (
                  <button
                    type="button"
                    className={`btn btn--compact${bggIncomplete ? " btn--primary" : " btn--ghost"}`}
                    disabled={busy}
                    onClick={onBggUpdate}
                  >
                    {t("games.bggUpdateOnCard")}
                  </button>
                ) : !game.bgg_id && game.is_active ? (
                  <span className="form-hint game-card__bgg-hint">{t("games.bggLinkOnCard")}</span>
                ) : null}
                <button
                  type="button"
                  className="btn btn--ghost btn--compact"
                  disabled={busy}
                  onClick={() => setEditing(true)}
                >
                  {t("games.edit")}
                </button>
                {game.is_active ? (
                  <button
                    type="button"
                    className="btn btn--danger btn--compact"
                    disabled={busy}
                    onClick={onDeactivate}
                  >
                    {t("games.deactivate")}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="btn btn--primary btn--compact"
                    disabled={busy}
                    onClick={onReactivate}
                  >
                    {t("games.reactivate")}
                  </button>
                )}
              </div>
            ) : null}
          </>
        )}
      </div>
    </li>
  );
}
