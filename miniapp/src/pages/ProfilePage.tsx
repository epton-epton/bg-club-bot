import { useCallback, useState } from "react";

import { api } from "../api/client";
import { Chip } from "../components/Chip";
import { ErrorState } from "../components/ErrorState";
import { FormPickerShell } from "../components/FormPickerShell";
import { LoadingState } from "../components/LoadingState";
import { ProfileSettings } from "../components/ProfileSettings";
import { SectionHeader } from "../components/SectionHeader";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import { useMe } from "../hooks/useMe";
import type { TableBooking, Visit } from "../types/api";
import {
  formatBookingStatus,
  formatDateParts,
  formatDateTime,
  formatVisitSource,
  toDatetimeLocalValue,
} from "../utils/format";

function defaultStartsAt(): string {
  const date = new Date();
  date.setHours(date.getHours() + 2, 0, 0, 0);
  return toDatetimeLocalValue(date.toISOString());
}

interface ProfilePageProps {
  onBack: () => void;
  onOpenAdmin?: () => void;
}

export function ProfilePage({ onBack, onOpenAdmin }: ProfilePageProps) {
  const { t } = useAppSettings();
  const { isAdmin, displayName } = useMe();
  const [reloadKey, setReloadKey] = useState(0);
  const [actionError, setActionError] = useState<string | null>(null);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  const { data: membership, loading: membershipLoading } = useAsyncData(
    () => api.getMyMembership(),
    [reloadKey],
  );
  const { data: visits, loading: visitsLoading } = useAsyncData(
    () => api.getMyVisits(),
    [reloadKey],
  );
  const { data: bookings, loading: bookingsLoading, error: bookingsError } = useAsyncData(
    () => api.getMyBookings(),
    [reloadKey],
  );

  const [showBookingForm, setShowBookingForm] = useState(false);
  const [startsAt, setStartsAt] = useState(defaultStartsAt);
  const [guestCount, setGuestCount] = useState("2");
  const [bookingNote, setBookingNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleCreateBooking(event: React.FormEvent) {
    event.preventDefault();
    setActionError(null);
    setSubmitting(true);
    try {
      await api.createBooking({
        starts_at: new Date(startsAt).toISOString(),
        guest_count: Number(guestCount),
        note: bookingNote.trim() || null,
      });
      setShowBookingForm(false);
      setBookingNote("");
      setStartsAt(defaultStartsAt());
      refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : t("profile.createBookingError"));
    } finally {
      setSubmitting(false);
    }
  }

  if (bookingsLoading || membershipLoading || visitsLoading) {
    return <LoadingState />;
  }

  if (bookingsError) {
    return <ErrorState message={bookingsError ?? t("profile.loadError")} />;
  }

  return (
    <section className="page">
      <header className="page-header page-header--profile">
        <div className="page-header__toolbar">
          <button type="button" className="page-back" onClick={onBack}>
            {t("common.back")}
          </button>
          <div className="page-header__toolbar-actions">
            {isAdmin && onOpenAdmin ? (
              <button type="button" className="btn btn--ghost btn--compact" onClick={onOpenAdmin}>
                {t("profile.openAdmin")}
              </button>
            ) : null}
            <button
              type="button"
              className="btn btn--primary btn--compact"
              onClick={() => setShowBookingForm((v) => !v)}
            >
              {showBookingForm ? t("common.cancel") : t("profile.booking")}
            </button>
          </div>
        </div>
        <div className="profile-header__title">
          <h1>{t("profile.title")}</h1>
          {isAdmin ? <span className="profile-admin-badge">{t("profile.admin")}</span> : null}
        </div>
        {displayName ? <p className="page-subtitle">{displayName}</p> : null}
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}

      <ProfileSettings />

      {showBookingForm ? (
        <form className="panel form-panel" onSubmit={handleCreateBooking}>
          <h2 className="form-panel__title">{t("profile.bookingFormTitle")}</h2>
          <p className="form-hint">{t("profile.bookingHint")}</p>

          <label className="form-field">
            <span className="form-label">{t("profile.datetime")}</span>
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
            <span className="form-label">{t("profile.guestCount")}</span>
            <input
              className="form-input"
              type="number"
              min={1}
              max={50}
              value={guestCount}
              onChange={(e) => setGuestCount(e.target.value)}
              required
            />
          </label>

          <label className="form-field">
            <span className="form-label">{t("profile.noteOptional")}</span>
            <textarea
              className="form-input form-input--textarea"
              value={bookingNote}
              onChange={(e) => setBookingNote(e.target.value)}
              rows={2}
              maxLength={1000}
            />
          </label>

          <button type="submit" className="btn btn--primary" disabled={submitting}>
            {submitting ? t("profile.submitting") : t("profile.submitBooking")}
          </button>
        </form>
      ) : null}

      <SectionHeader title={t("profile.membership")} />
      {membership ? (
        <article className="card card--accent">
          <div className="profile-stat-row">
            <strong>
              {t("profile.membershipBalance", {
                remaining: membership.visits_remaining,
                total: membership.total_visits,
              })}
            </strong>
            <Chip tone="cyan">{t("profile.visitsLeft")}</Chip>
          </div>
          {membership.note ? <p className="profile-note">{membership.note}</p> : null}
        </article>
      ) : (
        <p className="empty-hint">{t("profile.noMembership")}</p>
      )}

      <SectionHeader title={t("profile.myBookings")} />
      {bookings?.length ? (
        <ul className="card-list">
          {bookings.map((booking) => (
            <BookingCard key={booking.id} booking={booking} />
          ))}
        </ul>
      ) : (
        <p className="empty-hint">{t("profile.noBookings")}</p>
      )}

      <SectionHeader title={t("profile.visits")} />
      {visits?.length ? (
        <ul className="card-list card-list--compact">
          {visits.map((visit) => (
            <VisitRow key={visit.id} visit={visit} />
          ))}
        </ul>
      ) : (
        <p className="empty-hint">{t("profile.noVisits")}</p>
      )}
    </section>
  );
}

function BookingCard({ booking }: { booking: TableBooking }) {
  const { t, locale } = useAppSettings();
  const date = formatDateParts(booking.starts_at, locale);
  const tone =
    booking.status === "confirmed" ? "cyan" : booking.status === "cancelled" ? "pink" : undefined;

  return (
    <li className="card">
      <div className="session-card__header">
        <h2>
          {date.day} {date.month} · {date.time}
        </h2>
        <Chip tone={tone}>{formatBookingStatus(booking.status, t)}</Chip>
      </div>
      <p className="session-card__meta">
        {booking.guest_count} {t("profile.people")}
      </p>
      {booking.note ? <p className="session-card__note">{booking.note}</p> : null}
    </li>
  );
}

function VisitRow({ visit }: { visit: Visit }) {
  const { t, locale } = useAppSettings();
  return (
    <li className="card card--compact">
      <div className="profile-visit-row">
        <span>{formatDateTime(visit.checked_in_at, locale)}</span>
        <Chip>{formatVisitSource(visit.source, t)}</Chip>
      </div>
    </li>
  );
}
