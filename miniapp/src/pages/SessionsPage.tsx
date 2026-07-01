import { useCallback, useState } from "react";



import { api } from "../api/client";

import { Chip } from "../components/Chip";

import { ErrorState } from "../components/ErrorState";

import { FormPickerShell } from "../components/FormPickerShell";

import { LoadingState } from "../components/LoadingState";

import { useAppSettings } from "../contexts/AppSettingsContext";

import { useAsyncData } from "../hooks/useAsyncData";

import { useMe } from "../hooks/useMe";

import type { GameSession } from "../types/api";

import { formatDateParts, formatSessionStatus, toDatetimeLocalValue } from "../utils/format";
import { coverImageStyle } from "../utils/coverImage";



type GameMode = "catalog" | "custom";



function defaultStartsAt(): string {

  const date = new Date();

  date.setHours(date.getHours() + 2, 0, 0, 0);

  return toDatetimeLocalValue(date.toISOString());

}



export function SessionsPage() {

  const { t } = useAppSettings();
  const { isAdmin } = useMe();

  const [reloadKey, setReloadKey] = useState(0);

  const [showForm, setShowForm] = useState(false);

  const [actionError, setActionError] = useState<string | null>(null);

  const [busyId, setBusyId] = useState<number | null>(null);



  const { data: sessions, loading, error } = useAsyncData(() => api.getSessions(), [reloadKey]);

  const { data: games } = useAsyncData(() => api.getGames(), []);



  const [gameMode, setGameMode] = useState<GameMode>("catalog");

  const [gameId, setGameId] = useState("");

  const [customTitle, setCustomTitle] = useState("");

  const [startsAt, setStartsAt] = useState(defaultStartsAt);

  const [maxPlayers, setMaxPlayers] = useState("4");

  const [note, setNote] = useState("");

  const [submitting, setSubmitting] = useState(false);



  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);



  async function runAction(id: number, action: () => Promise<unknown>) {

    setActionError(null);

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



  async function handleCreate(event: React.FormEvent) {

    event.preventDefault();

    setActionError(null);

    setSubmitting(true);

    try {

      await api.createSession({

        starts_at: new Date(startsAt).toISOString(),

        max_players: Number(maxPlayers),

        note: note.trim() || null,

        game_id: gameMode === "catalog" ? Number(gameId) : null,

        custom_game_title: gameMode === "custom" ? customTitle.trim() : null,

      });

      setShowForm(false);

      setCustomTitle("");

      setNote("");

      setStartsAt(defaultStartsAt());

      refresh();

    } catch (err) {

      setActionError(err instanceof Error ? err.message : t("sessions.createError"));

    } finally {

      setSubmitting(false);

    }

  }



  if (loading) {

    return <LoadingState />;

  }



  if (error || !sessions) {

    return <ErrorState message={error ?? t("sessions.loadError")} />;

  }



  return (

    <section className="page">

      <header className="page-header page-header--row">

        <div>

          <h1>{t("sessions.title")}</h1>

          <p className="page-subtitle">{t("sessions.subtitle")}</p>

        </div>

        <button

          type="button"

          className="btn btn--primary btn--compact"

          onClick={() => setShowForm((v) => !v)}

        >

          {showForm ? t("common.cancel") : t("sessions.create")}

        </button>

      </header>



      {actionError ? <p className="form-error">{actionError}</p> : null}



      {showForm ? (

        <form className="panel form-panel" onSubmit={handleCreate}>

          <div className="form-field">

            <span className="form-label">{t("sessions.game")}</span>

            <div className="chip-row">

              <button

                type="button"

                className={gameMode === "catalog" ? "chip chip--cyan" : "chip"}

                onClick={() => setGameMode("catalog")}

              >

                {t("sessions.fromCatalog")}

              </button>

              <button

                type="button"

                className={gameMode === "custom" ? "chip chip--pink" : "chip"}

                onClick={() => setGameMode("custom")}

              >

                {t("sessions.customGame")}

              </button>

            </div>

          </div>



          {gameMode === "catalog" ? (

            <label className="form-field">

              <span className="form-label">{t("sessions.selectGame")}</span>

              <select

                className="form-input"

                value={gameId}

                onChange={(e) => setGameId(e.target.value)}

                required

              >

                <option value="">—</option>

                {games?.map((game) => (

                  <option key={game.id} value={game.id}>

                    {game.title}

                  </option>

                ))}

              </select>

            </label>

          ) : (

            <label className="form-field">

              <span className="form-label">{t("sessions.gameTitle")}</span>

              <input

                className="form-input"

                value={customTitle}

                onChange={(e) => setCustomTitle(e.target.value)}

                placeholder={t("sessions.gameTitlePlaceholder")}

                required

                maxLength={255}

              />

            </label>

          )}



          <label className="form-field">

            <span className="form-label">{t("sessions.datetime")}</span>

            <FormPickerShell>
              <input

                className="form-input"

                type="datetime-local"

                value={startsAt}

                onChange={(e) => setStartsAt(e.target.value)}

                required

              />
            </FormPickerShell>

          </label>



          <label className="form-field">

            <span className="form-label">{t("sessions.maxPlayers")}</span>

            <input

              className="form-input"

              type="number"

              min={2}

              max={20}

              value={maxPlayers}

              onChange={(e) => setMaxPlayers(e.target.value)}

              required

            />

          </label>



          <label className="form-field">

            <span className="form-label">{t("sessions.noteOptional")}</span>

            <textarea

              className="form-input form-input--textarea"

              value={note}

              onChange={(e) => setNote(e.target.value)}

              rows={2}

              maxLength={1000}

            />

          </label>



          <button type="submit" className="btn btn--primary" disabled={submitting}>

            {submitting ? t("sessions.creating") : t("sessions.createTable")}

          </button>

        </form>

      ) : null}



      {sessions.length ? (

        <ul className="card-list">

          {sessions.map((item) => (

            <SessionCard

              key={item.id}

              session={item}

              isAdmin={isAdmin}

              busy={busyId === item.id}

              onJoin={() => runAction(item.id, () => api.joinSession(item.id))}

              onLeave={() => runAction(item.id, () => api.leaveSession(item.id))}

              onCancel={() => runAction(item.id, () => api.cancelSession(item.id))}

              onAdminDelete={() => runAction(item.id, () => api.adminDeleteSession(item.id))}

            />

          ))}

        </ul>

      ) : (

        <p className="empty-hint">{t("sessions.empty")}</p>

      )}

    </section>

  );

}



interface SessionCardProps {

  session: GameSession;

  isAdmin: boolean;

  busy: boolean;

  onJoin: () => void;

  onLeave: () => void;

  onCancel: () => void;

  onAdminDelete: () => void;

}



function SessionCard({

  session,

  isAdmin,

  busy,

  onJoin,

  onLeave,

  onCancel,

  onAdminDelete,

}: SessionCardProps) {

  const { t, locale } = useAppSettings();

  const date = formatDateParts(session.starts_at, locale);

  const spotsLeft = session.max_players - session.participant_count;

  const canJoin = session.status === "open" && !session.is_joined;

  const canLeave = session.is_joined && !session.is_creator;



  return (

    <li

      className={

        session.cover_url

          ? "card session-card session-card--cover cover-card"

          : "card session-card session-card--cover session-card--cover-empty"

      }

      style={session.cover_url ? coverImageStyle(session.cover_url) : undefined}

    >

      {session.cover_url ? <div className="cover-card__bg" aria-hidden /> : null}

      <div className="session-card__overlay" />

      <div className="session-card__body">

        <div className="session-card__header">

          <h2>{session.title}</h2>

          <Chip tone={session.status === "full" ? "pink" : "cyan"}>

            {formatSessionStatus(session.status, t)}

          </Chip>

        </div>



        <div className="chip-row">

          <Chip>{`${date.day} ${date.month} · ${date.time}`}</Chip>

          <Chip>

            {t("sessions.players", {

              current: session.participant_count,

              max: session.max_players,

            })}

          </Chip>

        </div>



        <p className="session-card__meta">

          {t("sessions.organizer")}: {session.creator_name}

          {spotsLeft > 0 && session.status === "open"

            ? ` · ${t("sessions.spotsLeft", { n: spotsLeft })}`

            : null}

        </p>



        {session.note ? <p className="session-card__note">{session.note}</p> : null}



        {session.participants.length ? (

          <p className="session-card__players">

            {session.participants.map((p) => p.display_name).join(", ")}

          </p>

        ) : null}



        <div className="session-card__actions">

          {canJoin ? (

            <button type="button" className="btn btn--primary" disabled={busy} onClick={onJoin}>

              {t("sessions.join")}

            </button>

          ) : null}

          {canLeave ? (

            <button type="button" className="btn btn--ghost" disabled={busy} onClick={onLeave}>

              {t("sessions.leave")}

            </button>

          ) : null}

          {session.is_creator ? (

            <button type="button" className="btn btn--ghost" disabled={busy} onClick={onCancel}>

              {t("sessions.cancelSession")}

            </button>

          ) : null}

          {isAdmin ? (

            <button type="button" className="btn btn--danger" disabled={busy} onClick={onAdminDelete}>

              {t("common.delete")}

            </button>

          ) : null}

        </div>

      </div>

    </li>

  );

}


