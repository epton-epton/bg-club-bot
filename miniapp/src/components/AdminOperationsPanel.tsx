import { useState } from "react";

import { api } from "../api/client";
import { Chip } from "./Chip";
import { SectionHeader } from "./SectionHeader";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import type { AdminUser, TableBooking, Visit, VisitSource } from "../types/api";
import { formatBookingStatus, formatDateTime, formatVisitSource } from "../utils/format";

interface AdminOperationsPanelProps {
  bookings: TableBooking[];
  visits: Visit[];
  busyId: number | null;
  onBookingAction: (id: number, action: () => Promise<unknown>) => void;
  onRefresh: () => void;
  onError: (message: string | null) => void;
}

export function AdminOperationsPanel({
  bookings,
  visits,
  busyId,
  onBookingAction,
  onRefresh,
  onError,
}: AdminOperationsPanelProps) {
  const { t, locale } = useAppSettings();
  const [userQuery, setUserQuery] = useState("");
  const [searchResults, setSearchResults] = useState<AdminUser[] | null>(null);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [searching, setSearching] = useState(false);
  const [reloadUserKey, setReloadUserKey] = useState(0);

  const { data: allGuests, loading: guestsLoading } = useAsyncData(
    () => api.adminListGuests(),
    [reloadUserKey],
  );

  const { data: activeMemberships, loading: membershipsLoading } = useAsyncData(
    () => api.adminListMemberships(),
    [reloadUserKey],
  );

  function selectGuest(userId: number, displayName?: string | null) {
    const guest = allGuests?.find((u) => u.id === userId);
    if (guest) {
      setSelectedUser(guest);
      return;
    }
    setSelectedUser({
      id: userId,
      telegram_id: 0,
      username: null,
      first_name: displayName,
      last_name: null,
      display_name: displayName ?? `User #${userId}`,
      role: "guest",
    });
  }

  const { data: selectedMembership } = useAsyncData(
    () =>
      selectedUser ? api.adminGetUserMembership(selectedUser.id) : Promise.resolve(null),
    [selectedUser?.id, reloadUserKey],
  );
  const [totalVisits, setTotalVisits] = useState("10");
  const [extendVisits, setExtendVisits] = useState("5");
  const [visitSource, setVisitSource] = useState<VisitSource>("membership");
  const [adminBusy, setAdminBusy] = useState(false);

  async function handleSearch(event: React.FormEvent) {
    event.preventDefault();
    if (!userQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setSearching(true);
    onError(null);
    try {
      const results = await api.adminSearchUsers(userQuery.trim());
      setSearchResults(results);
      setSelectedUser(results[0] ?? null);
    } catch (err) {
      onError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setSearching(false);
    }
  }

  function showAllGuests() {
    setUserQuery("");
    setSearchResults(null);
  }

  async function handleIssueMembership(event: React.FormEvent) {
    event.preventDefault();
    if (!selectedUser) return;
    setAdminBusy(true);
    onError(null);
    try {
      await api.adminCreateMembership({
        user_id: selectedUser.id,
        total_visits: Number(totalVisits),
      });
      setReloadUserKey((k) => k + 1);
      onRefresh();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setAdminBusy(false);
    }
  }

  async function handleCheckIn() {
    if (!selectedUser) return;
    setAdminBusy(true);
    onError(null);
    try {
      await api.adminCreateVisit({ user_id: selectedUser.id, source: visitSource });
      setReloadUserKey((k) => k + 1);
      onRefresh();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setAdminBusy(false);
    }
  }

  const pendingBookings = bookings.filter((b) => b.status === "submitted");
  const confirmedBookings = bookings.filter((b) => b.status === "confirmed");

  return (
    <>
      <SectionHeader title={t("admin.bookings")} />
      {pendingBookings.length ? (
        <ul className="card-list">
          {pendingBookings.map((booking) => (
            <li key={booking.id} className="card">
              <div className="session-card__header">
                <h2>{booking.user_name ?? `User #${booking.user_id}`}</h2>
                <Chip>{formatBookingStatus(booking.status, t)}</Chip>
              </div>
              <p className="session-card__meta">
                {formatDateTime(booking.starts_at, locale)} · {booking.guest_count}{" "}
                {t("profile.people")}
              </p>
              {booking.note ? <p className="session-card__note">{booking.note}</p> : null}
              <div className="session-card__actions">
                <button
                  type="button"
                  className="btn btn--primary"
                  disabled={busyId === booking.id}
                  onClick={() =>
                    onBookingAction(booking.id, () =>
                      api.adminUpdateBookingStatus(booking.id, "confirmed"),
                    )
                  }
                >
                  {t("admin.confirm")}
                </button>
                <button
                  type="button"
                  className="btn btn--danger"
                  disabled={busyId === booking.id}
                  onClick={() =>
                    onBookingAction(booking.id, () =>
                      api.adminUpdateBookingStatus(booking.id, "cancelled"),
                    )
                  }
                >
                  {t("common.cancel")}
                </button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty-hint">{t("admin.noPendingBookings")}</p>
      )}

      <SectionHeader title={t("admin.confirmedBookings")} />
      {confirmedBookings.length ? (
        <ul className="card-list">
          {confirmedBookings.map((booking) => (
            <li key={booking.id} className="card">
              <div className="session-card__header">
                <h2>{booking.user_name ?? `User #${booking.user_id}`}</h2>
                <Chip tone="cyan">{formatBookingStatus(booking.status, t)}</Chip>
              </div>
              <p className="session-card__meta">
                {formatDateTime(booking.starts_at, locale)} · {booking.guest_count}{" "}
                {t("profile.people")}
              </p>
              {booking.note ? <p className="session-card__note">{booking.note}</p> : null}
              <div className="session-card__actions">
                <button
                  type="button"
                  className="btn btn--danger"
                  disabled={busyId === booking.id}
                  onClick={() =>
                    onBookingAction(booking.id, () =>
                      api.adminUpdateBookingStatus(booking.id, "cancelled"),
                    )
                  }
                >
                  {t("admin.cancelBooking")}
                </button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty-hint">{t("admin.noConfirmedBookings")}</p>
      )}

      <SectionHeader title={t("admin.guests")} />
      <div className="admin-guests-stack">
      <p className="form-hint">{t("admin.guestListHint")}</p>

      {membershipsLoading ? <p className="empty-hint">{t("common.loading")}</p> : null}
      {!membershipsLoading && activeMemberships?.length ? (
        <details className="admin-guest-spoiler">
          <summary className="admin-guest-spoiler__summary">
            {t("admin.activeMemberships", { n: activeMemberships.length })}
          </summary>
          <ul className="card-list card-list--compact admin-guest-list admin-guest-spoiler__list">
            {activeMemberships.map((membership) => (
              <li key={membership.id}>
                <button
                  type="button"
                  className={
                    selectedUser?.id === membership.user_id
                      ? "admin-guest-row admin-guest-row--selected"
                      : "admin-guest-row"
                  }
                  onClick={() => selectGuest(membership.user_id, membership.user_name)}
                >
                  <span className="admin-guest-row__name">
                    {membership.user_name ?? `User #${membership.user_id}`}
                  </span>
                  <span className="admin-guest-row__meta">
                    {t("admin.membershipSummary", {
                      remaining: membership.visits_remaining,
                      total: membership.total_visits,
                    })}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
      {!membershipsLoading && !activeMemberships?.length ? (
        <p className="empty-hint">{t("admin.noActiveMemberships")}</p>
      ) : null}

      <form className="panel form-panel" onSubmit={handleSearch}>
        <label className="form-field">
          <span className="form-label">{t("admin.searchUser")}</span>
          <input
            className="form-input"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder={t("admin.searchPlaceholder")}
          />
        </label>
        <div className="session-card__actions">
          <button type="submit" className="btn btn--ghost" disabled={searching}>
            {searching ? t("admin.searching") : t("admin.search")}
          </button>
          {searchResults ? (
            <button type="button" className="btn btn--ghost" onClick={showAllGuests}>
              {t("admin.showAllGuests")}
            </button>
          ) : null}
        </div>
      </form>

      {searchResults ? (
        <>
          <p className="form-hint">{t("admin.searchResultsHint", { n: searchResults.length })}</p>
          {searchResults.length ? (
            <ul className="card-list card-list--compact admin-guest-list">
              {searchResults.map((user) => (
                <li key={user.id}>
                  <button
                    type="button"
                    className={
                      selectedUser?.id === user.id
                        ? "admin-guest-row admin-guest-row--selected"
                        : "admin-guest-row"
                    }
                    onClick={() => setSelectedUser(user)}
                  >
                    <span className="admin-guest-row__name">{user.display_name}</span>
                    <span className="admin-guest-row__meta">
                      {user.username
                        ? `@${user.username}`
                        : t("admin.telegramId", { id: user.telegram_id })}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-hint">{t("admin.noSearchResults")}</p>
          )}
        </>
      ) : null}

      {guestsLoading ? <p className="empty-hint">{t("common.loading")}</p> : null}
      {!guestsLoading && allGuests?.length ? (
        <details className="admin-guest-spoiler">
          <summary className="admin-guest-spoiler__summary">
            {t("admin.allGuestsToggle", { n: allGuests.length })}
          </summary>
          <ul className="card-list card-list--compact admin-guest-list admin-guest-spoiler__list">
            {allGuests.map((user) => (
              <li key={user.id}>
                <button
                  type="button"
                  className={
                    selectedUser?.id === user.id
                      ? "admin-guest-row admin-guest-row--selected"
                      : "admin-guest-row"
                  }
                  onClick={() => setSelectedUser(user)}
                >
                  <span className="admin-guest-row__name">{user.display_name}</span>
                  <span className="admin-guest-row__meta">
                    {user.username
                      ? `@${user.username}`
                      : t("admin.telegramId", { id: user.telegram_id })}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
      {!guestsLoading && !allGuests?.length && !searchResults ? (
        <p className="empty-hint">{t("admin.noGuests")}</p>
      ) : null}

      {selectedUser ? (
        <div className="panel form-panel admin-guest-panel">
          <div className="admin-guest-panel__meta">
            <p className="form-hint">
              {t("admin.selectedLabel", { name: selectedUser.display_name })}
            </p>
            {selectedMembership ? (
              <p className="form-hint">
                {t("admin.membershipSummary", {
                  remaining: selectedMembership.visits_remaining,
                  total: selectedMembership.total_visits,
                })}
              </p>
            ) : (
              <p className="form-hint">{t("admin.noMembership")}</p>
            )}
          </div>

          <form className="admin-guest-panel__section" onSubmit={handleIssueMembership}>
            <label className="form-field">
              <span className="form-label">{t("admin.issueMembership")}</span>
              <input
                className="form-input"
                type="number"
                min={1}
                max={500}
                value={totalVisits}
                onChange={(e) => setTotalVisits(e.target.value)}
                required
              />
            </label>
            <button type="submit" className="btn btn--primary" disabled={adminBusy}>
              {t("admin.issue")}
            </button>
          </form>

          <div className="admin-guest-panel__section form-field">
            <span className="form-label">{t("admin.checkIn")}</span>
            <div className="chip-row chip-row--field">
              <button
                type="button"
                className={visitSource === "membership" ? "chip chip--cyan" : "chip"}
                onClick={() => setVisitSource("membership")}
              >
                {t("admin.membershipSource")}
              </button>
              <button
                type="button"
                className={visitSource === "walk_in" ? "chip chip--pink" : "chip"}
                onClick={() => setVisitSource("walk_in")}
              >
                {t("admin.walkIn")}
              </button>
            </div>
            <button
              type="button"
              className="btn btn--primary"
              disabled={adminBusy}
              onClick={handleCheckIn}
            >
              {t("admin.markVisit")}
            </button>
          </div>

          <form
            className="admin-guest-panel__section"
            onSubmit={async (e) => {
              e.preventDefault();
              if (!selectedUser) return;
              setAdminBusy(true);
              onError(null);
              try {
                const userMembership = await api.adminGetUserMembership(selectedUser.id);
                if (!userMembership) {
                  onError(t("admin.noActiveMembership"));
                  return;
                }
                await api.adminExtendMembership(userMembership.id, Number(extendVisits));
                setReloadUserKey((k) => k + 1);
                onRefresh();
              } catch (err) {
                onError(err instanceof Error ? err.message : t("common.error"));
              } finally {
                setAdminBusy(false);
              }
            }}
          >
            <label className="form-field">
              <span className="form-label">{t("admin.extendMembership")}</span>
              <input
                className="form-input"
                type="number"
                min={1}
                max={500}
                value={extendVisits}
                onChange={(e) => setExtendVisits(e.target.value)}
              />
            </label>
            <button type="submit" className="btn btn--ghost" disabled={adminBusy}>
              {t("admin.extend")}
            </button>
          </form>

          {selectedMembership ? (
            <button
              type="button"
              className="btn btn--danger admin-guest-panel__cancel"
              disabled={adminBusy}
              onClick={async () => {
                if (!selectedMembership) return;
                setAdminBusy(true);
                onError(null);
                try {
                  await api.adminCancelMembership(selectedMembership.id);
                  setReloadUserKey((k) => k + 1);
                  onRefresh();
                } catch (err) {
                  onError(err instanceof Error ? err.message : t("common.error"));
                } finally {
                  setAdminBusy(false);
                }
              }}
            >
              {t("admin.cancelMembership")}
            </button>
          ) : null}
        </div>
      ) : null}
      </div>

      <SectionHeader title={t("admin.recentVisits")} />
      {visits.length ? (
        <ul className="card-list card-list--compact">
          {visits.slice(0, 10).map((visit) => (
            <li key={visit.id} className="card card--compact">
              <div className="profile-visit-row">
                <span>
                  {visit.user_name} · {formatDateTime(visit.checked_in_at, locale)}
                </span>
                <Chip>{formatVisitSource(visit.source, t)}</Chip>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty-hint">{t("admin.noVisits")}</p>
      )}
    </>
  );
}
