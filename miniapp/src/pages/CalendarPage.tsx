import { useCallback, useMemo, useState } from "react";

import { api } from "../api/client";
import { Chip } from "../components/Chip";
import { ErrorState } from "../components/ErrorState";
import { FormPickerShell } from "../components/FormPickerShell";
import { LoadingState } from "../components/LoadingState";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import { useMe } from "../hooks/useMe";
import type { Locale } from "../i18n";
import type { Event } from "../types/api";
import { formatDateParts, formatEventType, formatMonthYear, toDatetimeLocalValue } from "../utils/format";

interface CalendarPageProps {
  onBack: () => void;
}

function defaultStartsAt(): string {
  const date = new Date();
  date.setDate(date.getDate() + 7);
  date.setHours(18, 0, 0, 0);
  return toDatetimeLocalValue(date.toISOString());
}

function groupEventsByMonth(
  events: Event[],
  locale: Locale,
): { month: string; items: Event[] }[] {
  const groups = new Map<string, Event[]>();
  for (const event of events) {
    const key = formatMonthYear(event.starts_at, locale);
    const bucket = groups.get(key);
    if (bucket) {
      bucket.push(event);
    } else {
      groups.set(key, [event]);
    }
  }
  return Array.from(groups.entries()).map(([month, items]) => ({ month, items }));
}

export function CalendarPage({ onBack }: CalendarPageProps) {
  const { t, locale } = useAppSettings();
  const { isAdmin } = useMe();
  const [reloadKey, setReloadKey] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const fetchEvents = useCallback(
    () => (isAdmin ? api.adminGetEvents() : api.getEvents(100)),
    [isAdmin],
  );

  const { data: events, loading, error } = useAsyncData(fetchEvents, [reloadKey, isAdmin]);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startsAt, setStartsAt] = useState(defaultStartsAt);
  const [endsAt, setEndsAt] = useState("");
  const [eventType, setEventType] = useState("other");
  const [submitting, setSubmitting] = useState(false);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  const grouped = useMemo(() => {
    const sorted = [...(events ?? [])].sort(
      (a, b) => new Date(a.starts_at).getTime() - new Date(b.starts_at).getTime(),
    );
    return groupEventsByMonth(sorted, locale);
  }, [events, locale]);

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
      await api.adminCreateEvent({
        title: title.trim(),
        description: description.trim() || null,
        starts_at: new Date(startsAt).toISOString(),
        ends_at: endsAt ? new Date(endsAt).toISOString() : null,
        event_type: eventType,
      });
      setShowForm(false);
      setTitle("");
      setDescription("");
      setEndsAt("");
      setStartsAt(defaultStartsAt());
      refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("calendar.createError"));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error || !events) {
    return <ErrorState message={error ?? t("calendar.loadError")} />;
  }

  return (
    <section className="page">
      <header className="page-header page-header--row">
        <div>
          <button type="button" className="page-back" onClick={onBack}>
            {t("common.back")}
          </button>
          <h1>{t("calendar.title")}</h1>
          <p className="page-subtitle">{t("calendar.subtitle")}</p>
        </div>
        {isAdmin ? (
          <button
            type="button"
            className="btn btn--primary btn--compact"
            onClick={() => setShowForm((v) => !v)}
          >
            {showForm ? t("calendar.hide") : t("calendar.create")}
          </button>
        ) : null}
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}

      {isAdmin && showForm ? (
        <form className="panel form-panel" onSubmit={handleCreate}>
          <div className="form-field">
            <label className="form-label" htmlFor="event-title">
              {t("calendar.name")}
            </label>
            <input
              id="event-title"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label className="form-label" htmlFor="event-description">
              {t("calendar.description")}
            </label>
            <textarea
              id="event-description"
              className="form-input form-input--textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label className="form-label" htmlFor="event-type">
              {t("calendar.type")}
            </label>
            <select
              id="event-type"
              className="form-input"
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
            >
              <option value="tournament">{t("calendar.types.tournament")}</option>
              <option value="open_game">{t("calendar.types.open_game")}</option>
              <option value="workshop">{t("calendar.types.workshop")}</option>
              <option value="other">{t("calendar.types.other")}</option>
            </select>
          </div>
          <div className="form-field">
            <label className="form-label" htmlFor="event-starts">
              {t("calendar.starts")}
            </label>
            <FormPickerShell>
              <input
                id="event-starts"
                type="datetime-local"
                className="form-input"
                value={startsAt}
                onChange={(e) => setStartsAt(e.target.value)}
                required
              />
            </FormPickerShell>
          </div>
          <div className="form-field">
            <label className="form-label" htmlFor="event-ends">
              {t("calendar.endsOptional")}
            </label>
            <FormPickerShell>
              <input
                id="event-ends"
                type="datetime-local"
                className="form-input"
                value={endsAt}
                onChange={(e) => setEndsAt(e.target.value)}
              />
            </FormPickerShell>
          </div>
          <button type="submit" className="btn btn--primary" disabled={submitting}>
            {submitting ? t("calendar.saving") : t("calendar.createBtn")}
          </button>
        </form>
      ) : null}

      {grouped.length ? (
        grouped.map((group) => (
          <div key={group.month} className="calendar-group">
            <h2 className="calendar-group__title">{group.month}</h2>
            <div className="panel">
              <ul className="row-list">
                {group.items.map((event) => {
                  const date = formatDateParts(event.starts_at, locale);
                  const isCancelled = event.status === "cancelled";
                  return (
                    <li key={event.id} className="row-item">
                      <div className="row-item__body">
                        {editingId === event.id ? (
                          <EventEditForm
                            event={event}
                            onCancel={() => setEditingId(null)}
                            onSaved={() => {
                              setEditingId(null);
                              refresh();
                            }}
                            onError={setActionError}
                          />
                        ) : (
                          <>
                            <div className="row-item__top">
                              <strong>{event.title}</strong>
                              {!isCancelled ? (
                                <span className="status-dot status-dot--active" />
                              ) : (
                                <Chip tone="pink">{t("calendar.cancelled")}</Chip>
                              )}
                            </div>
                            <div className="chip-row">
                              <Chip>{`${date.day} ${date.month}`}</Chip>
                              <Chip tone="cyan">{formatEventType(event.event_type, t)}</Chip>
                              <Chip>{date.time}</Chip>
                            </div>
                            {event.description ? (
                              <p className="row-item__desc">{event.description}</p>
                            ) : null}
                            {isAdmin ? (
                              <div className="row-item__actions">
                                <button
                                  type="button"
                                  className="btn btn--ghost btn--compact"
                                  disabled={busyId === event.id}
                                  onClick={() => setEditingId(event.id)}
                                >
                                  {t("calendar.edit")}
                                </button>
                                {!isCancelled ? (
                                  <button
                                    type="button"
                                    className="btn btn--ghost btn--compact"
                                    disabled={busyId === event.id}
                                    onClick={() =>
                                      runAction(event.id, () =>
                                        api.adminUpdateEvent(event.id, { status: "cancelled" }),
                                      )
                                    }
                                  >
                                    {t("calendar.cancelEvent")}
                                  </button>
                                ) : null}
                                <button
                                  type="button"
                                  className="btn btn--danger btn--compact"
                                  disabled={busyId === event.id}
                                  onClick={() =>
                                    runAction(event.id, () => api.adminDeleteEvent(event.id))
                                  }
                                >
                                  {t("common.delete")}
                                </button>
                              </div>
                            ) : null}
                          </>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        ))
      ) : (
        <p className="empty-hint">{t("calendar.empty")}</p>
      )}
    </section>
  );
}

interface EventEditFormProps {
  event: Event;
  onCancel: () => void;
  onSaved: () => void;
  onError: (message: string | null) => void;
}

function EventEditForm({ event, onCancel, onSaved, onError }: EventEditFormProps) {
  const { t } = useAppSettings();
  const [title, setTitle] = useState(event.title);
  const [description, setDescription] = useState(event.description ?? "");
  const [startsAt, setStartsAt] = useState(toDatetimeLocalValue(event.starts_at));
  const [endsAt, setEndsAt] = useState(
    event.ends_at ? toDatetimeLocalValue(event.ends_at) : "",
  );
  const [eventType, setEventType] = useState(event.event_type);
  const [submitting, setSubmitting] = useState(false);

  async function handleSave(formEvent: React.FormEvent) {
    formEvent.preventDefault();
    onError(null);
    setSubmitting(true);
    try {
      await api.adminUpdateEvent(event.id, {
        title: title.trim(),
        description: description.trim() || null,
        starts_at: new Date(startsAt).toISOString(),
        ends_at: endsAt ? new Date(endsAt).toISOString() : null,
        event_type: eventType,
      });
      onSaved();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("calendar.updateError"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="content-edit-form" onSubmit={handleSave}>
      <div className="form-field">
        <label className="form-label" htmlFor={`event-edit-title-${event.id}`}>
          {t("calendar.name")}
        </label>
        <input
          id={`event-edit-title-${event.id}`}
          className="form-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div className="form-field">
        <label className="form-label" htmlFor={`event-edit-description-${event.id}`}>
          {t("calendar.description")}
        </label>
        <textarea
          id={`event-edit-description-${event.id}`}
          className="form-input form-input--textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="form-field">
        <label className="form-label" htmlFor={`event-edit-type-${event.id}`}>
          {t("calendar.type")}
        </label>
        <select
          id={`event-edit-type-${event.id}`}
          className="form-input"
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
        >
          <option value="tournament">{t("calendar.types.tournament")}</option>
          <option value="open_game">{t("calendar.types.open_game")}</option>
          <option value="workshop">{t("calendar.types.workshop")}</option>
          <option value="other">{t("calendar.types.other")}</option>
        </select>
      </div>
      <div className="form-field">
        <label className="form-label" htmlFor={`event-edit-starts-${event.id}`}>
          {t("calendar.starts")}
        </label>
        <FormPickerShell>
          <input
            id={`event-edit-starts-${event.id}`}
            type="datetime-local"
            className="form-input"
            value={startsAt}
            onChange={(e) => setStartsAt(e.target.value)}
            required
          />
        </FormPickerShell>
      </div>
      <div className="form-field">
        <label className="form-label" htmlFor={`event-edit-ends-${event.id}`}>
          {t("calendar.endsOptional")}
        </label>
        <FormPickerShell>
          <input
            id={`event-edit-ends-${event.id}`}
            type="datetime-local"
            className="form-input"
            value={endsAt}
            onChange={(e) => setEndsAt(e.target.value)}
          />
        </FormPickerShell>
      </div>
      <div className="session-card__actions">
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? t("calendar.saving") : t("common.save")}
        </button>
        <button type="button" className="btn btn--ghost" onClick={onCancel}>
          {t("common.cancel")}
        </button>
      </div>
    </form>
  );
}
