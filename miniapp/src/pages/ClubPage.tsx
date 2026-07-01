import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { SectionHeader } from "../components/SectionHeader";
import { useAppSettings } from "../contexts/AppSettingsContext";
import { useClub } from "../hooks/useClub";
import { useMe } from "../hooks/useMe";
import { computeOpenStatus, formatOpenStatusLabel } from "../utils/clubHours";

const CLUB_TIMEZONES = [
  "Europe/Kyiv",
  "Europe/Moscow",
  "Europe/Warsaw",
  "Europe/Berlin",
  "Europe/London",
  "UTC",
] as const;

export function ClubPage() {
  const { t } = useAppSettings();
  const { isAdmin } = useMe();
  const { club, loading, error, refreshClub } = useClub();
  const [showAdmin, setShowAdmin] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionInfo, setActionInfo] = useState<string | null>(null);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !club) {
    return <ErrorState message={error ?? t("club.loadError")} />;
  }

  return (
    <section className="page">
      <header className="page-header page-header--row page-header--club">
        <div>
          <h1>{club.name}</h1>
          <p className="page-subtitle">{t("club.subtitle")}</p>
        </div>
        {isAdmin ? (
          <button
            type="button"
            className="btn btn--primary btn--compact"
            onClick={() => setShowAdmin((value) => !value)}
          >
            {showAdmin ? t("club.hideAdmin") : t("club.manage")}
          </button>
        ) : null}
      </header>

      {actionError ? <p className="form-error">{actionError}</p> : null}
      {actionInfo ? <p className="form-hint form-hint--success">{actionInfo}</p> : null}

      {isAdmin && showAdmin ? (
        <ClubAdminPanel
          club={club}
          onSaved={async () => {
            setActionError(null);
            setActionInfo(t("club.saved"));
            await refreshClub();
          }}
          onError={setActionError}
        />
      ) : null}

      <div className="hero-card">
        <span className="hero-card__emoji">🎲</span>
        <div>
          <strong>{club.name}</strong>
          <p className="hero-card__text">{club.address}</p>
        </div>
      </div>

      <SectionHeader title={t("club.contacts")} />
      <div className="panel">
        <div className="info-row">
          <span className="info-row__icon">📍</span>
          <div>
            <strong>{t("club.address")}</strong>
            <p>{club.address}</p>
          </div>
        </div>
        <div className="info-row">
          <span className="info-row__icon">🕐</span>
          <div>
            <strong>{t("club.hours")}</strong>
            <p className="multiline">{club.hours}</p>
          </div>
        </div>
      </div>

      <SectionHeader title={t("club.rules")} />
      <article className="card card--accent">
        <p className="multiline">{club.rules}</p>
      </article>
    </section>
  );
}

interface ClubAdminPanelProps {
  club: NonNullable<ReturnType<typeof useClub>["club"]>;
  onSaved: () => Promise<void>;
  onError: (message: string | null) => void;
}

function ClubAdminPanel({ club, onSaved, onError }: ClubAdminPanelProps) {
  const { t, locale } = useAppSettings();
  const [name, setName] = useState(club.name);
  const [address, setAddress] = useState(club.address);
  const [hours, setHours] = useState(club.hours);
  const [timezone, setTimezone] = useState(club.timezone ?? "Europe/Kyiv");
  const [statusOverride, setStatusOverride] = useState(club.open_status_override ?? "");
  const [rules, setRules] = useState(club.rules);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setName(club.name);
    setAddress(club.address);
    setHours(club.hours);
    setTimezone(club.timezone ?? "Europe/Kyiv");
    setStatusOverride(club.open_status_override ?? "");
    setRules(club.rules);
  }, [club]);

  const statusPreview = useMemo(
    () => formatOpenStatusLabel(computeOpenStatus(hours, statusOverride, timezone, locale), t),
    [hours, statusOverride, timezone, locale, t],
  );

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    onError(null);
    try {
      await api.updateClub({
        name: name.trim(),
        address: address.trim(),
        hours: hours.trim(),
        timezone: timezone.trim(),
        rules: rules.trim(),
        open_status_override: statusOverride.trim() || null,
        clear_status_override: !statusOverride.trim(),
      });
      await onSaved();
    } catch (err) {
      onError(err instanceof Error ? err.message : t("club.saveError"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="admin-club">
      <h2 className="admin-club__heading">{t("club.adminTitle")}</h2>
      <form className="panel form-panel admin-club__panel" onSubmit={handleSubmit}>
        <label className="form-field">
          <span className="form-label">{t("club.name")}</span>
          <input className="form-input" value={name} onChange={(e) => setName(e.target.value)} required />
        </label>

        <label className="form-field">
          <span className="form-label">{t("club.address")}</span>
          <input
            className="form-input"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            required
          />
        </label>

        <label className="form-field">
          <span className="form-label">{t("club.hours")}</span>
          <textarea
            className="form-input form-input--textarea"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            rows={4}
            required
          />
          <p className="form-hint">{t("club.hoursHint")}</p>
        </label>

        <label className="form-field">
          <span className="form-label">{t("club.timezone")}</span>
          <select
            className="form-input"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
          >
            {CLUB_TIMEZONES.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
            {!CLUB_TIMEZONES.includes(timezone as (typeof CLUB_TIMEZONES)[number]) ? (
              <option value={timezone}>{timezone}</option>
            ) : null}
          </select>
          <p className="form-hint">{t("club.timezoneHint")}</p>
        </label>

        <label className="form-field">
          <span className="form-label">{t("club.statusOverride")}</span>
          <input
            className="form-input"
            value={statusOverride}
            onChange={(e) => setStatusOverride(e.target.value)}
            placeholder={t("club.statusOverridePlaceholder")}
          />
          <p className="form-hint">{t("club.statusOverrideHint")}</p>
        </label>

        <div className="admin-club__preview">
          <span className="form-label">{t("club.statusPreview")}</span>
          <p className="admin-club__preview-text">{statusPreview}</p>
        </div>

        <label className="form-field">
          <span className="form-label">{t("club.rules")}</span>
          <textarea
            className="form-input form-input--textarea"
            value={rules}
            onChange={(e) => setRules(e.target.value)}
            rows={5}
            required
          />
        </label>

        <button type="submit" className="btn btn--primary admin-club__save" disabled={saving}>
          {saving ? t("club.saving") : t("club.save")}
        </button>
      </form>
    </div>
  );
}
