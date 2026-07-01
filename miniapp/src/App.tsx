import { useState } from "react";

import { BottomNav, type TabId } from "./components/BottomNav";
import { ClubStatusBadge } from "./components/ClubStatusBadge";
import { useAppSettings } from "./contexts/AppSettingsContext";
import { useClub } from "./hooks/useClub";
import { useMe } from "./hooks/useMe";
import { useTelegram } from "./hooks/useTelegram";
import { AdminPage } from "./pages/AdminPage";
import { CalendarPage } from "./pages/CalendarPage";
import { ClubPage } from "./pages/ClubPage";
import { FeedPage } from "./pages/FeedPage";
import { GamesPage } from "./pages/GamesPage";
import { NewsPage } from "./pages/NewsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { SessionsPage } from "./pages/SessionsPage";

type OverlayId = "calendar" | "news" | "profile" | "admin";

function renderTab(tab: TabId, onOpenCalendar: () => void, onOpenNews: () => void) {
  switch (tab) {
    case "club":
      return <ClubPage />;
    case "games":
      return <GamesPage />;
    case "sessions":
      return <SessionsPage />;
    case "feed":
    default:
      return <FeedPage onOpenCalendar={onOpenCalendar} onOpenNews={onOpenNews} />;
  }
}

export default function App() {
  const [tab, setTab] = useState<TabId>("feed");
  const [overlay, setOverlay] = useState<OverlayId | null>(null);
  useTelegram();
  const { t } = useAppSettings();
  const { isAdmin } = useMe();
  const { club } = useClub();

  function handleAdminNavigate(nextTab: TabId, nextOverlay?: "calendar" | "news") {
    setTab(nextTab);
    setOverlay(nextOverlay ?? null);
  }

  return (
    <div className="app">
      <header className="app-bar">
        <img className="app-bar__logo" src="/logo.png" alt={t("app.logoAlt")} />
        <div className="app-bar__spacer" />
        <ClubStatusBadge status={club?.open_status} />
        {isAdmin ? (
          <button
            type="button"
            className="app-bar__badge app-bar__admin"
            onClick={() => setOverlay("admin")}
          >
            {t("app.admin")}
          </button>
        ) : null}
        <button
          type="button"
          className="app-bar__badge app-bar__profile"
          onClick={() => setOverlay("profile")}
        >
          {t("app.profile")}
        </button>
      </header>

      <main className="app-main">
        {overlay === "calendar" ? (
          <CalendarPage onBack={() => setOverlay(null)} />
        ) : overlay === "news" ? (
          <NewsPage onBack={() => setOverlay(null)} />
        ) : overlay === "profile" ? (
          <ProfilePage onBack={() => setOverlay(null)} onOpenAdmin={() => setOverlay("admin")} />
        ) : overlay === "admin" ? (
          <AdminPage onBack={() => setOverlay(null)} onNavigate={handleAdminNavigate} />
        ) : (
          renderTab(tab, () => setOverlay("calendar"), () => setOverlay("news"))
        )}
      </main>

      {!overlay ? <BottomNav active={tab} onChange={setTab} /> : null}
    </div>
  );
}
