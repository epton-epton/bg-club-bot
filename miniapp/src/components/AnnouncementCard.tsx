import type { ReactNode } from "react";

import { useAppSettings } from "../contexts/AppSettingsContext";
import type { Announcement } from "../types/api";
import { coverImageStyle } from "../utils/coverImage";

const DEFAULT_PINNED_IMAGE = "/announcement-default.svg";

interface AnnouncementHeroProps {
  announcement: Announcement;
  actions?: ReactNode;
}

export function AnnouncementHero({ announcement, actions }: AnnouncementHeroProps) {
  const { t } = useAppSettings();
  const customImage = announcement.image_url?.trim() || null;
  const backgroundUrl = customImage ?? DEFAULT_PINNED_IMAGE;

  return (
    <article className="cover-card pinned-hero" style={coverImageStyle(backgroundUrl)}>
      <div className="cover-card__bg" aria-hidden />
      <div className="pinned-hero__overlay" aria-hidden />
      <div className="pinned-hero__content">
        <span className="pinned-hero__badge">{t("news.important")}</span>
        <h2 className="pinned-hero__title">{announcement.title}</h2>
        <p className="pinned-hero__body">{announcement.body}</p>
        {actions ? <div className="pinned-hero__actions">{actions}</div> : null}
      </div>
    </article>
  );
}

interface AnnouncementRowProps {
  announcement: Announcement;
  meta?: ReactNode;
  topExtra?: ReactNode;
  actions?: ReactNode;
}

export function AnnouncementRow({ announcement, meta, topExtra, actions }: AnnouncementRowProps) {
  const imageUrl = announcement.image_url?.trim() || null;
  const hasImage = imageUrl !== null;

  if (hasImage) {
    return (
      <div className="cover-card announcement-row announcement-row--image" style={coverImageStyle(imageUrl)}>
        <div className="cover-card__bg" aria-hidden />
        <div className="announcement-row__overlay" aria-hidden />
        <div className="announcement-row__content">
          <div className="row-item__top">
            <strong>{announcement.title}</strong>
            {topExtra}
          </div>
          <p className="row-item__desc">{announcement.body}</p>
          {meta ? <span className="row-item__meta">{meta}</span> : null}
          {actions}
        </div>
      </div>
    );
  }

  return (
    <div className="row-item__body">
      <div className="row-item__top">
        <strong>{announcement.title}</strong>
        {topExtra}
      </div>
      <p className="row-item__desc">{announcement.body}</p>
      {meta ? <span className="row-item__meta">{meta}</span> : null}
      {actions}
    </div>
  );
}

interface AnnouncementImagePreviewProps {
  imageUrl: string;
}

export function AnnouncementImagePreview({ imageUrl }: AnnouncementImagePreviewProps) {
  const { t } = useAppSettings();
  const trimmed = imageUrl.trim();
  if (!trimmed) {
    return null;
  }

  return (
    <div className="announcement-image-preview">
      <span className="announcement-image-preview__label">{t("news.imagePreview")}</span>
      <div className="cover-card announcement-image-preview__frame" style={coverImageStyle(trimmed)}>
        <div className="cover-card__bg" aria-hidden />
        <div className="announcement-image-preview__overlay" aria-hidden />
      </div>
    </div>
  );
}
