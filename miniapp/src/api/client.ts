import type {
  AdminUser,
  Announcement,
  AnnouncementCreatePayload,
  AnnouncementUpdatePayload,
  BggSearchItem,
  BggSyncResult,
  BookingCreatePayload,
  Club,
  ClubUpdatePayload,
  Event,
  EventCreatePayload,
  EventUpdatePayload,
  Feed,
  Game,
  GameCreatePayload,
  GameSession,
  GameUpdatePayload,
  Me,
  MePreferencesUpdate,
  Membership,
  MembershipCreatePayload,
  SessionCreatePayload,
  TableBooking,
  Visit,
  VisitCreatePayload,
} from "../types/api";

const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

/** Prod miniapp: same-origin /api via nginx. Dev: Vite proxy or VITE_API_URL. */
function apiUrl(path: string): string {
  if (import.meta.env.PROD) {
    return path;
  }
  return API_BASE ? `${API_BASE}${path}` : path;
}

function getAuthHeader(): string | null {
  const initData = window.Telegram?.WebApp?.initData;
  if (initData) {
    return `tma ${initData}`;
  }
  if (import.meta.env.DEV) {
    return "dev";
  }
  return null;
}

interface RequestOptions {
  auth?: boolean;
  method?: string;
  body?: unknown;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.auth) {
    const auth = getAuthHeader();
    if (auth) {
      headers.Authorization = auth;
    }
  }
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error(
      import.meta.env.DEV
        ? "Backend недоступен. Запустите API на http://localhost:8000 (см. README)."
        : "Backend недоступен. Проверьте, что API запущен на Railway.",
    );
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as { detail?: string | { msg?: string }[] };
      if (typeof payload.detail === "string") {
        detail = payload.detail;
      } else if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
        detail = payload.detail[0].msg;
      }
    } catch {
      // keep statusText
    }
    throw new Error(detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function uploadFile(path: string, file: File): Promise<{ url: string }> {
  const headers: Record<string, string> = {};
  const auth = getAuthHeader();
  if (auth) {
    headers.Authorization = auth;
  }

  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      method: "POST",
      headers,
      body: formData,
    });
  } catch {
    throw new Error(
      import.meta.env.DEV
        ? "Backend недоступен. Запустите API на http://localhost:8000 (см. README)."
        : "Backend недоступен. Проверьте, что API запущен на Railway.",
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = (await response.json()) as { detail?: string | { msg?: string }[] };
      if (typeof payload.detail === "string") {
        detail = payload.detail;
      } else if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
        detail = payload.detail[0].msg;
      }
    } catch {
      // keep statusText
    }
    throw new Error(detail);
  }

  return response.json() as Promise<{ url: string }>;
}

export const api = {
  getMe: () => request<Me>("/api/v1/me", { auth: true }),
  updatePreferences: (payload: MePreferencesUpdate) =>
    request<Me>("/api/v1/me/preferences", { auth: true, method: "PATCH", body: payload }),
  getClub: () => request<Club>("/api/v1/club"),
  updateClub: (payload: ClubUpdatePayload) =>
    request<Club>("/api/v1/admin/club", { auth: true, method: "PATCH", body: payload }),
  getGames: () => request<Game[]>("/api/v1/games"),
  adminGetGames: () => request<Game[]>("/api/v1/admin/games", { auth: true }),
  createGame: (payload: GameCreatePayload) =>
    request<Game>("/api/v1/games", { auth: true, method: "POST", body: payload }),
  updateGame: (id: number, payload: GameUpdatePayload) =>
    request<Game>(`/api/v1/games/${id}`, { auth: true, method: "PATCH", body: payload }),
  deactivateGame: (id: number) =>
    request<Game>(`/api/v1/games/${id}`, { auth: true, method: "DELETE" }),
  bggSearch: (q: string) =>
    request<BggSearchItem[]>(`/api/v1/games/bgg/search?q=${encodeURIComponent(q)}`, {
      auth: true,
    }),
  bggImport: (bggId: number, gameId?: number) =>
    request<Game>(
      `/api/v1/games/bgg/${bggId}${gameId ? `?game_id=${gameId}` : ""}`,
      { auth: true, method: "POST" },
    ),
  bggSyncAll: () =>
    request<BggSyncResult>("/api/v1/games/bgg/sync", { auth: true, method: "POST" }),
  getAnnouncements: (limit = 50) =>
    request<Announcement[]>(`/api/v1/announcements?limit=${limit}`),
  getEvents: (limit = 50) => request<Event[]>(`/api/v1/events?limit=${limit}`),
  getFeed: () => request<Feed>("/api/v1/feed"),
  getSessions: () => request<GameSession[]>("/api/v1/sessions", { auth: true }),
  createSession: (payload: SessionCreatePayload) =>
    request<GameSession>("/api/v1/sessions", {
      auth: true,
      method: "POST",
      body: payload,
    }),
  joinSession: (id: number) =>
    request<GameSession>(`/api/v1/sessions/${id}/join`, { auth: true, method: "POST" }),
  leaveSession: (id: number) =>
    request<GameSession>(`/api/v1/sessions/${id}/leave`, { auth: true, method: "DELETE" }),
  cancelSession: (id: number) =>
    request<GameSession>(`/api/v1/sessions/${id}/cancel`, { auth: true, method: "PATCH" }),
  adminDeleteSession: (id: number) =>
    request<void>(`/api/v1/admin/sessions/${id}`, { auth: true, method: "DELETE" }),
  adminGetEvents: () => request<Event[]>("/api/v1/admin/events", { auth: true }),
  adminCreateEvent: (payload: EventCreatePayload) =>
    request<Event>("/api/v1/admin/events", { auth: true, method: "POST", body: payload }),
  adminUpdateEvent: (id: number, payload: EventUpdatePayload) =>
    request<Event>(`/api/v1/admin/events/${id}`, { auth: true, method: "PATCH", body: payload }),
  adminDeleteEvent: (id: number) =>
    request<void>(`/api/v1/admin/events/${id}`, { auth: true, method: "DELETE" }),
  adminGetAnnouncements: () =>
    request<Announcement[]>("/api/v1/admin/announcements", { auth: true }),
  adminCreateAnnouncement: (payload: AnnouncementCreatePayload) =>
    request<Announcement>("/api/v1/admin/announcements", {
      auth: true,
      method: "POST",
      body: payload,
    }),
  adminUpdateAnnouncement: (id: number, payload: AnnouncementUpdatePayload) =>
    request<Announcement>(`/api/v1/admin/announcements/${id}`, {
      auth: true,
      method: "PATCH",
      body: payload,
    }),
  adminDeleteAnnouncement: (id: number) =>
    request<void>(`/api/v1/admin/announcements/${id}`, { auth: true, method: "DELETE" }),
  uploadAnnouncementImage: (file: File) =>
    uploadFile("/api/v1/admin/uploads/announcement-image", file),
  getMyBookings: () => request<TableBooking[]>("/api/v1/bookings/me", { auth: true }),
  createBooking: (payload: BookingCreatePayload) =>
    request<TableBooking>("/api/v1/bookings", { auth: true, method: "POST", body: payload }),
  getMyMembership: () => request<Membership | null>("/api/v1/me/membership", { auth: true }),
  getMyVisits: () => request<Visit[]>("/api/v1/me/visits", { auth: true }),
  adminGetBookings: () => request<TableBooking[]>("/api/v1/admin/bookings", { auth: true }),
  adminUpdateBookingStatus: (id: number, status: TableBooking["status"]) =>
    request<TableBooking>(`/api/v1/admin/bookings/${id}`, {
      auth: true,
      method: "PATCH",
      body: { status },
    }),
  adminListGuests: () => request<AdminUser[]>("/api/v1/admin/users", { auth: true }),
  adminListMemberships: () => request<Membership[]>("/api/v1/admin/memberships", { auth: true }),
  adminSearchUsers: (q: string) =>
    request<AdminUser[]>(`/api/v1/admin/users?q=${encodeURIComponent(q)}`, { auth: true }),
  adminGetUserMembership: (userId: number) =>
    request<Membership | null>(`/api/v1/admin/users/${userId}/membership`, { auth: true }),
  adminCreateMembership: (payload: MembershipCreatePayload) =>
    request<Membership>("/api/v1/admin/memberships", {
      auth: true,
      method: "POST",
      body: payload,
    }),
  adminExtendMembership: (id: number, addVisits: number) =>
    request<Membership>(`/api/v1/admin/memberships/${id}/extend`, {
      auth: true,
      method: "PATCH",
      body: { add_visits: addVisits },
    }),
  adminCancelMembership: (id: number) =>
    request<Membership>(`/api/v1/admin/memberships/${id}/cancel`, {
      auth: true,
      method: "PATCH",
    }),
  adminGetVisits: () => request<Visit[]>("/api/v1/admin/visits", { auth: true }),
  adminCreateVisit: (payload: VisitCreatePayload) =>
    request<Visit>("/api/v1/admin/visits", { auth: true, method: "POST", body: payload }),
};
