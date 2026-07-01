import { api } from "../api/client";

import { AnnouncementRow } from "../components/AnnouncementCard";
import { Chip } from "../components/Chip";

import { ErrorState } from "../components/ErrorState";

import { LoadingState } from "../components/LoadingState";

import { PinnedAnnouncementHero } from "../components/PinnedAnnouncementHero";

import { SectionHeader } from "../components/SectionHeader";

import { useAppSettings } from "../contexts/AppSettingsContext";

import { useAsyncData } from "../hooks/useAsyncData";

import { formatDateParts, formatEventType } from "../utils/format";



interface FeedPageProps {

  onOpenCalendar: () => void;

  onOpenNews: () => void;

}



export function FeedPage({ onOpenCalendar, onOpenNews }: FeedPageProps) {

  const { t, locale } = useAppSettings();

  const { data, loading, error } = useAsyncData(() => api.getFeed(), []);



  if (loading) {

    return <LoadingState />;

  }



  if (error || !data) {

    return <ErrorState message={error ?? t("feed.loadError")} />;

  }



  const pinnedAnnouncement = data.announcements.find((item) => item.is_pinned);

  const regularAnnouncements = pinnedAnnouncement

    ? data.announcements.filter((item) => item.id !== pinnedAnnouncement.id)

    : data.announcements;



  return (

    <section className="page">

      <header className="page-header">

        <h1>{t("feed.title")}</h1>

      </header>



      {pinnedAnnouncement ? <PinnedAnnouncementHero announcement={pinnedAnnouncement} /> : null}



      <SectionHeader title={t("feed.events")} action={t("feed.calendar")} onAction={onOpenCalendar} />



      {data.events.length ? (

        <div className="panel">

          <ul className="row-list">

            {data.events.map((event) => {

              const date = formatDateParts(event.starts_at, locale);

              return (

                <li key={event.id} className="row-item">
                  <div className="row-item__body">
                    <div className="row-item__top">
                      <strong>{event.title}</strong>
                      <span className="status-dot status-dot--active" />
                    </div>
                    <div className="chip-row">
                      <Chip>{`${date.day} ${date.month}`}</Chip>
                      <Chip tone="cyan">{formatEventType(event.event_type, t)}</Chip>
                      <Chip>{date.time}</Chip>
                    </div>

                    {event.description ? (

                      <p className="row-item__desc">{event.description}</p>

                    ) : null}

                  </div>

                </li>

              );

            })}

          </ul>

        </div>

      ) : (

        <p className="empty-hint">{t("feed.noEvents")}</p>

      )}



      <SectionHeader title={t("feed.news")} action={t("common.all")} onAction={onOpenNews} />



      {regularAnnouncements.length ? (

        <div className="panel">

          <ul className="row-list">

            {regularAnnouncements.map((item) => {

              const date = formatDateParts(item.published_at, locale);

              return (

                <li key={item.id} className="row-item row-item--news">
                  <AnnouncementRow
                    announcement={item}
                    meta={
                      <>
                        {date.day} {date.month} · {date.time}
                      </>
                    }
                  />
                </li>

              );

            })}

          </ul>

        </div>

      ) : (

        <p className="empty-hint">{t("feed.noNews")}</p>

      )}

    </section>

  );

}


