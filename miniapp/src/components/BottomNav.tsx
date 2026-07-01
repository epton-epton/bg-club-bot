import { useAppSettings } from "../contexts/AppSettingsContext";



export type TabId = "feed" | "sessions" | "games" | "club";



interface BottomNavProps {

  active: TabId;

  onChange: (tab: TabId) => void;

}



const tabs: { id: TabId; labelKey: string; icon: string }[] = [

  { id: "feed", labelKey: "nav.feed", icon: "🏠" },

  { id: "sessions", labelKey: "nav.sessions", icon: "🪑" },

  { id: "games", labelKey: "nav.games", icon: "🎲" },

  { id: "club", labelKey: "nav.club", icon: "ℹ️" },

];



export function BottomNav({ active, onChange }: BottomNavProps) {

  const { t } = useAppSettings();



  return (

    <nav className="bottom-nav" aria-label={t("nav.aria")}>

      {tabs.map((tab) => (

        <button

          key={tab.id}

          type="button"

          className={active === tab.id ? "bottom-nav__item is-active" : "bottom-nav__item"}

          onClick={() => onChange(tab.id)}

        >

          <span className="bottom-nav__icon">{tab.icon}</span>

          <span className="bottom-nav__label">{t(tab.labelKey)}</span>

        </button>

      ))}

    </nav>

  );

}


