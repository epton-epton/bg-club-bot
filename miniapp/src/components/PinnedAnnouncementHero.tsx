import type { ReactNode } from "react";

import type { Announcement } from "../types/api";

import { AnnouncementHero } from "./AnnouncementCard";

interface PinnedAnnouncementHeroProps {
  announcement: Announcement;
  actions?: ReactNode;
}

export function PinnedAnnouncementHero({ announcement, actions }: PinnedAnnouncementHeroProps) {
  return <AnnouncementHero announcement={announcement} actions={actions} />;
}
