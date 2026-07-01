import { useCallback, useMemo, useState } from "react";

import { api } from "../api/client";
import { AnnouncementImageField } from "../components/AnnouncementImageField";
import { AnnouncementRow } from "../components/AnnouncementCard";
import { Chip } from "../components/Chip";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { PinnedAnnouncementHero } from "../components/PinnedAnnouncementHero";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import { useMe } from "../hooks/useMe";
import { formatDateParts } from "../utils/format";
import type { Announcement } from "../types/api";

interface NewsPageProps {
  onBack: () => void;
}

export function NewsPage({ onBack }: NewsPageProps) {
  const { t, locale } = useAppSettings();
  const { isAdmin } = useMe();
  const [reloadKey, setReloadKey] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const fetchAnnouncements = useCallback(
    () => (isAdmin ? api.adminGetAnnouncements() : api.getAnnouncements(100)),
    [isAdmin],
  );

  const { data: announcements, loading, error } = useAsyncData(fetchAnnouncements, [
    reloadKey,
    isAdmin,
  ]);

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [isPinned, setIsPinned] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  const { pinned, regular } = useMemo(() => {
    if (!announcements) {
      return { pinned: null, regular: [] };
    }
    const published = isAdmin
      ? announcements
      : announcements.filter((item) => item.status === "published");
    const pinnedItem = published.find((item) => item.is_pinned) ?? null;
    const rest = pinnedItem
      ? published.filter((item) => item.id !== pinnedItem.id)
      : published;
    return { pinned: pinnedItem, regular: rest };
  }, [announcements, isAdmin]);

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
      await api.adminCreateAnnouncement({
        title: title.trim(),
        body: body.trim(),
        image_url: imageUrl.trim() || null,
        is_pinned: isPinned,
      });
      setShowForm(false);
      setTitle("");
      setBody("");
      setImageUrl("");
      setIsPinned(false);
      refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("news.createError"));
    } finally {
      setSubmitting(false);
    }
  }

  function renderAdminActions(item: NonNullable<typeof announcements>[number]) {
    return (
      <div className="row-item__actions">
        <button
          type="button"
          className="btn btn--ghost btn--compact"
          disabled={busyId === item.id}
          onClick={() => setEditingId(item.id)}
        >
          {t("news.edit")}
        </button>
        {item.status === "published" ? (
          <button
            type="button"
            className="btn btn--ghost btn--compact"
            disabled={busyId === item.id}
            onClick={() =>
              runAction(item.id, () =>
                api.adminUpdateAnnouncement(item.id, { status: "archived" }),
              )
            }
          >
            {t("news.archive")}
          </button>
        ) : item.status === "archived" ? (
          <button
            type="button"
            className="btn btn--ghost btn--compact"
            disabled={busyId === item.id}
            onClick={() =>
              runAction(item.id, () =>
                api.adminUpdateAnnouncement(item.id, { status: "published" }),
              )
            }
          >
            {t("news.publishAgain")}
          </button>
        ) : null}
        <button
          type="button"
          className="btn btn--danger btn--compact"
          disabled={busyId === item.id}
          onClick={() => runAction(item.id, () => api.adminDeleteAnnouncement(item.id))}
        >
          {t("common.delete")}
        </button>
      </div>
    );
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error || !announcements) {
    return <ErrorState message={error ?? t("news.loadError")} />;
  }

  return (
    <section className="page">
      <header className="page-header page-header--row">
        <div>
          <button type="button" className="page-back" onClick={onBack}>
            {t("common.back")}
          </button>
          <h1>{t("news.title")}</h1>
          <p className="page-subtitle">{t("news.subtitle")}</p>
        </div>
        {isAdmin ? (
          <button
            type="button"
            className="btn btn--primary btn--compact"
            onClick={() => setShowForm((v) => !v)}
          >
            {showForm ? t("news.hide") : t("news.create")}
          </button>
        ) : null}
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}

      {isAdmin && showForm ? (
        <form className="panel form-panel" onSubmit={handleCreate}>
          <div className="form-field">
            <label className="form-label" htmlFor="news-title">
              {t("news.headline")}
            </label>
            <input
              id="news-title"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          <div className="form-field">
            <label className="form-label" htmlFor="news-body">
              {t("news.body")}
            </label>
            <textarea
              id="news-body"
              className="form-input form-input--textarea"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              required
            />
          </div>
          <AnnouncementImageField
            value={imageUrl}
            onChange={setImageUrl}
            onError={setActionError}
            inputId="news-image"
          />
          <label className="form-checkbox">
            <input
              type="checkbox"
              checked={isPinned}
              onChange={(e) => setIsPinned(e.target.checked)}
            />
            {t("news.pin")}
          </label>
          <button type="submit" className="btn btn--primary" disabled={submitting}>
            {submitting ? t("news.saving") : t("news.publish")}
          </button>
        </form>
      ) : null}

      {pinned ? (
        editingId === pinned.id ? (
          <AnnouncementEditForm
            announcement={pinned}
            onCancel={() => setEditingId(null)}
            onSaved={() => {
              setEditingId(null);
              refresh();
            }}
            onError={setActionError}
          />
        ) : (
          <PinnedAnnouncementHero
            announcement={pinned}
            actions={isAdmin ? renderAdminActions(pinned) : undefined}
          />
        )
      ) : null}

      {regular.length ? (
        <div className="panel">
          <ul className="row-list">
            {regular.map((item) => (
              <li key={item.id} className="row-item row-item--news">
                {editingId === item.id ? (
                  <AnnouncementEditForm
                    announcement={item}
                    onCancel={() => setEditingId(null)}
                    onSaved={() => {
                      setEditingId(null);
                      refresh();
                    }}
                    onError={setActionError}
                  />
                ) : (
                  <AnnouncementRow
                    announcement={item}
                    topExtra={
                      isAdmin && item.status !== "published" ? (
                        <Chip tone="pink">
                          {t(`news.statuses.${item.status}` as "news.statuses.published")}
                        </Chip>
                      ) : null
                    }
                    meta={
                      <>
                        {formatDateParts(item.published_at, locale).day}{" "}
                        {formatDateParts(item.published_at, locale).month} ·{" "}
                        {formatDateParts(item.published_at, locale).time}
                      </>
                    }
                    actions={isAdmin ? renderAdminActions(item) : undefined}
                  />
                )}
              </li>
            ))}
          </ul>
        </div>
      ) : !pinned ? (
        <p className="empty-hint">{t("news.empty")}</p>
      ) : null}
    </section>
  );
}

interface AnnouncementEditFormProps {
  announcement: Announcement;
  onCancel: () => void;
  onSaved: () => void;
  onError: (message: string | null) => void;
}

function AnnouncementEditForm({
  announcement,
  onCancel,
  onSaved,
  onError,
}: AnnouncementEditFormProps) {
  const { t } = useAppSettings();
  const [title, setTitle] = useState(announcement.title);
  const [body, setBody] = useState(announcement.body);
  const [imageUrl, setImageUrl] = useState(announcement.image_url ?? "");
  const [isPinned, setIsPinned] = useState(announcement.is_pinned);
  const [submitting, setSubmitting] = useState(false);

  async function handleSave(event: React.FormEvent) {
    event.preventDefault();
    onError(null);
    setSubmitting(true);
    try {
      await api.adminUpdateAnnouncement(announcement.id, {
        title: title.trim(),
        body: body.trim(),
        image_url: imageUrl.trim() || null,
        is_pinned: isPinned,
      });
      onSaved();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("news.updateError"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="panel form-panel content-edit-form" onSubmit={handleSave}>
      <div className="form-field">
        <label className="form-label" htmlFor={`news-edit-title-${announcement.id}`}>
          {t("news.headline")}
        </label>
        <input
          id={`news-edit-title-${announcement.id}`}
          className="form-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div className="form-field">
        <label className="form-label" htmlFor={`news-edit-body-${announcement.id}`}>
          {t("news.body")}
        </label>
        <textarea
          id={`news-edit-body-${announcement.id}`}
          className="form-input form-input--textarea"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          required
        />
      </div>
      <AnnouncementImageField
        value={imageUrl}
        onChange={setImageUrl}
        onError={onError}
        inputId={`news-edit-image-${announcement.id}`}
      />
      <label className="form-checkbox">
        <input
          type="checkbox"
          checked={isPinned}
          onChange={(e) => setIsPinned(e.target.checked)}
        />
        {t("news.pin")}
      </label>
      <div className="session-card__actions">
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? t("news.saving") : t("common.save")}
        </button>
        <button type="button" className="btn btn--ghost" onClick={onCancel}>
          {t("common.cancel")}
        </button>
      </div>
    </form>
  );
}
