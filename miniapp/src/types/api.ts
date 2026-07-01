export interface ClubOpenStatus {
  is_open: boolean | null;
  /** Admin override — shown as-is */
  label?: string;
  messageKey?: string;
  messageVars?: Record<string, string | number>;
}

export interface Club {
  id: number;
  name: string;
  address: string;
  hours: string;
  timezone?: string;
  open_status_override?: string | null;
  rules: string;
  updated_at: string;
  open_status?: ClubOpenStatus;
}

export interface ClubUpdatePayload {
  name?: string;
  address?: string;
  hours?: string;
  timezone?: string;
  open_status_override?: string | null;
  rules?: string;
  clear_status_override?: boolean;
}

export interface Game {
  id: number;
  bgg_id: number | null;
  title: string;
  image_url: string | null;
  cover_url: string | null;
  year_published: number | null;
  bgg_rating: number | null;
  bgg_rank: number | null;
  description: string | null;
  players_min: number | null;
  players_max: number | null;
  duration_minutes: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Announcement {
  id: number;
  title: string;
  body: string;
  image_url: string | null;
  published_at: string;
  is_pinned: boolean;
  status: string;
  created_at: string;
}

export interface Event {
  id: number;
  title: string;
  description: string | null;
  starts_at: string;
  ends_at: string | null;
  event_type: string;
  status: string;
  created_at: string;
}

export interface Feed {
  events: Event[];
  announcements: Announcement[];
}

export type AppLanguage = "ru" | "en" | "ua";
export type AppTheme = "synthwave" | "midnight" | "aurora" | "daylight";

export interface Me {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  role: "guest" | "admin";
  language: AppLanguage | null;
  theme: AppTheme | null;
}

export interface MePreferencesUpdate {
  language?: AppLanguage;
  theme?: AppTheme;
}

export type SessionStatus = "open" | "full" | "cancelled" | "completed";

export interface SessionParticipant {
  id: number;
  user_id: number;
  display_name: string;
  joined_at: string;
}

export interface GameSession {
  id: number;
  game_id: number | null;
  game_title: string | null;
  custom_game_title: string | null;
  title: string;
  starts_at: string;
  max_players: number;
  participant_count: number;
  status: SessionStatus;
  note: string | null;
  creator_id: number;
  creator_name: string;
  is_creator: boolean;
  is_joined: boolean;
  cover_url: string | null;
  participants: SessionParticipant[];
  created_at: string;
}

export interface SessionCreatePayload {
  game_id?: number | null;
  custom_game_title?: string | null;
  starts_at: string;
  max_players: number;
  note?: string | null;
}

export interface EventCreatePayload {
  title: string;
  description?: string | null;
  starts_at: string;
  ends_at?: string | null;
  event_type?: string;
  status?: string;
}

export interface EventUpdatePayload {
  title?: string;
  description?: string | null;
  starts_at?: string;
  ends_at?: string | null;
  event_type?: string;
  status?: string;
}

export interface AnnouncementCreatePayload {
  title: string;
  body: string;
  image_url?: string | null;
  published_at?: string | null;
  is_pinned?: boolean;
  status?: string;
}

export interface AnnouncementUpdatePayload {
  title?: string;
  body?: string;
  image_url?: string | null;
  published_at?: string | null;
  is_pinned?: boolean;
  status?: string;
}

export type BookingStatus = "submitted" | "confirmed" | "cancelled";

export interface TableBooking {
  id: number;
  user_id: number;
  user_name: string | null;
  starts_at: string;
  guest_count: number;
  status: BookingStatus;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface BookingCreatePayload {
  starts_at: string;
  guest_count: number;
  note?: string | null;
}

export type MembershipStatus = "active" | "exhausted" | "cancelled";

export interface Membership {
  id: number;
  user_id: number;
  user_name: string | null;
  total_visits: number;
  visits_used: number;
  visits_remaining: number;
  status: MembershipStatus;
  note: string | null;
  created_at: string;
  updated_at: string;
}

export interface MembershipCreatePayload {
  user_id: number;
  total_visits: number;
  note?: string | null;
}

export type VisitSource = "membership" | "walk_in";

export interface Visit {
  id: number;
  user_id: number;
  user_name: string | null;
  membership_id: number | null;
  source: VisitSource;
  checked_in_at: string;
  note: string | null;
  created_at: string;
}

export interface VisitCreatePayload {
  user_id: number;
  source: VisitSource;
  note?: string | null;
}

export interface AdminUser {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  display_name: string;
  role: "guest" | "admin";
}

export interface GameCreatePayload {
  title: string;
  description?: string | null;
  players_min?: number | null;
  players_max?: number | null;
  duration_minutes?: number | null;
}

export interface GameUpdatePayload {
  title?: string;
  description?: string | null;
  players_min?: number | null;
  players_max?: number | null;
  duration_minutes?: number | null;
  is_active?: boolean;
}

export interface BggSearchItem {
  bgg_id: number;
  title: string;
  year: number | null;
}

export interface BggSyncResult {
  synced: number;
  failed: number;
}
