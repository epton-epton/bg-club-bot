import { useCallback, useState } from "react";

import { api } from "../api/client";
import { AdminOperationsPanel } from "../components/AdminOperationsPanel";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useAsyncData } from "../hooks/useAsyncData";
import type { TabId } from "../components/BottomNav";

interface AdminPageProps {
  onBack: () => void;
  onNavigate: (tab: TabId, overlay?: "calendar" | "news") => void;
}

export function AdminPage({ onBack, onNavigate }: AdminPageProps) {
  const { t } = useAppSettings();
  const [reloadKey, setReloadKey] = useState(0);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const refresh = useCallback(() => setReloadKey((k) => k + 1), []);

  const { data: adminBookings } = useAsyncData(() => api.adminGetBookings(), [reloadKey]);
  const { data: adminVisits } = useAsyncData(() => api.adminGetVisits(), [reloadKey]);

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

  return (
    <section className="page">
      <header className="page-header page-header--profile">
        <div className="page-header__toolbar">
          <button type="button" className="page-back" onClick={onBack}>
            {t("common.back")}
          </button>
        </div>
        <h1>{t("admin.title")}</h1>
        <p className="page-subtitle">{t("admin.subtitle")}</p>
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}

      <div className="admin-shortcuts">
        <button
          type="button"
          className="admin-shortcut card"
          onClick={() => onNavigate("games")}
        >
          <strong>{t("admin.shortcuts.games")}</strong>
          <span className="admin-shortcut__hint">{t("admin.shortcuts.gamesHint")}</span>
        </button>
        <button
          type="button"
          className="admin-shortcut card"
          onClick={() => onNavigate("feed", "calendar")}
        >
          <strong>{t("admin.shortcuts.events")}</strong>
          <span className="admin-shortcut__hint">{t("admin.shortcuts.eventsHint")}</span>
        </button>
        <button
          type="button"
          className="admin-shortcut card"
          onClick={() => onNavigate("feed", "news")}
        >
          <strong>{t("admin.shortcuts.news")}</strong>
          <span className="admin-shortcut__hint">{t("admin.shortcuts.newsHint")}</span>
        </button>
        <button
          type="button"
          className="admin-shortcut card"
          onClick={() => onNavigate("sessions")}
        >
          <strong>{t("admin.shortcuts.sessions")}</strong>
          <span className="admin-shortcut__hint">{t("admin.shortcuts.sessionsHint")}</span>
        </button>
      </div>

      <AdminOperationsPanel
        bookings={adminBookings ?? []}
        visits={adminVisits ?? []}
        busyId={busyId}
        onBookingAction={runAction}
        onRefresh={refresh}
        onError={setActionError}
      />
    </section>
  );
}
