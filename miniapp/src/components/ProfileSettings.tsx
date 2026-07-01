import { useAppSettings } from "../contexts/AppSettingsContext";
import { LOCALES, THEMES, type Locale, type ThemeId } from "../i18n";

export function ProfileSettings() {
  const {
    t,
    locale,
    theme,
    settingsSaving,
    settingsSaved,
    settingsError,
    updatePreferences,
  } = useAppSettings();

  function handleLanguage(language: Locale) {
    void updatePreferences({ language });
  }

  function handleTheme(nextTheme: ThemeId) {
    void updatePreferences({ theme: nextTheme });
  }

  return (
    <div className="panel form-panel profile-settings">
      <h2 className="form-panel__title">{t("profile.settings")}</h2>

      <div className="form-field">
        <span className="form-label">{t("profile.language")}</span>
        <div className="chip-row chip-row--settings">
          {LOCALES.map((lang) => (
            <button
              key={lang}
              type="button"
              className={locale === lang ? "chip chip--cyan settings-chip" : "chip settings-chip"}
              disabled={settingsSaving}
              onClick={() => handleLanguage(lang)}
            >
              {t(`languages.${lang}`)}
            </button>
          ))}
        </div>
      </div>

      <div className="form-field">
        <span className="form-label">{t("profile.theme")}</span>
        <div className="theme-picker">
          {THEMES.map((themeId) => (
            <button
              key={themeId}
              type="button"
              className={theme === themeId ? "theme-picker__item is-active" : "theme-picker__item"}
              disabled={settingsSaving}
              onClick={() => handleTheme(themeId)}
            >
              <span className={`theme-picker__swatch theme-picker__swatch--${themeId}`} />
              <span className="theme-picker__label">{t(`themes.${themeId}`)}</span>
            </button>
          ))}
        </div>
      </div>

      {settingsSaving ? <p className="form-hint">{t("common.loading")}</p> : null}
      {settingsSaved ? <p className="form-hint form-hint--success">{t("common.saved")}</p> : null}
      {settingsError ? <p className="form-error">{settingsError}</p> : null}
    </div>
  );
}
