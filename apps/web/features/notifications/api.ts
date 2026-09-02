import { apiFetch } from "@/lib/apiClient";
import type { AppNotification, Invitation } from "@/types";

export const notificationsApi = {
  list: () => apiFetch<AppNotification[]>("/notifications"),
  unreadCount: () => apiFetch<{ count: number }>("/notifications/unread-count"),
  markRead: (id: string) => apiFetch<AppNotification>(`/notifications/${id}/read`, { method: "PATCH" }),
  markAllRead: () => apiFetch<void>("/notifications/read-all", { method: "PATCH" }),
};

export const invitationsApi = {
  list: () => apiFetch<Invitation[]>("/invitations"),
  accept: (id: string) => apiFetch<Invitation>(`/invitations/${id}/accept`, { method: "POST" }),
  reject: (id: string) => apiFetch<void>(`/invitations/${id}/reject`, { method: "POST" }),
};
