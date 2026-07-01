import { useId, useRef, useState } from "react";

import { api } from "../api/client";
import { useAppSettings } from "../contexts/AppSettingsContext";

import { AnnouncementImagePreview } from "./AnnouncementCard";

interface AnnouncementImageFieldProps {
  value: string;
  onChange: (url: string) => void;
  onError: (message: string | null) => void;
  inputId?: string;
}

export function AnnouncementImageField({
  value,
  onChange,
  onError,
  inputId,
}: AnnouncementImageFieldProps) {
  const { t } = useAppSettings();
  const autoId = useId();
  const fileInputId = inputId ?? autoId;
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }

    onError(null);
    setUploading(true);
    try {
      const result = await api.uploadAnnouncementImage(file);
      onChange(result.url);
    } catch (err) {
      onError(err instanceof Error ? err.message : t("news.imageUploadError"));
    } finally {
      setUploading(false);
    }
  }

  function handleRemove() {
    onChange("");
    onError(null);
  }

  return (
    <div className="form-field">
      <span className="form-label">{t("news.image")}</span>
      <div className="announcement-image-field">
        <input
          ref={fileInputRef}
          id={fileInputId}
          className="announcement-image-field__input"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <div className="announcement-image-field__actions">
          <button
            type="button"
            className="btn btn--ghost btn--compact"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? t("news.imageUploading") : t("news.pickImage")}
          </button>
          {value ? (
            <button
              type="button"
              className="btn btn--ghost btn--compact"
              onClick={handleRemove}
              disabled={uploading}
            >
              {t("news.removeImage")}
            </button>
          ) : null}
        </div>
        <p className="announcement-image-field__hint">{t("news.imageHint")}</p>
        {value ? <AnnouncementImagePreview imageUrl={value} /> : null}
      </div>
    </div>
  );
}
