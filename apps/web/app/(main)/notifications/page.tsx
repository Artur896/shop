"use client";

import { useToast } from "@/components/ToastProvider";
import { EmptyState } from "@/components/EmptyState";
import { Skeleton } from "@/components/Skeleton";
import {
  useAcceptInvitation,
  useInvitations,
  useMarkAllRead,
  useNotifications,
  useRejectInvitation,
} from "@/features/notifications/hooks";

function timeAgo(iso: string): string {
  const minutes = Math.round((Date.now() - new Date(iso).getTime()) / 60_000);
  if (minutes < 1) return "justo ahora";
  if (minutes < 60) return `hace ${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `hace ${hours} h`;
  return `hace ${Math.round(hours / 24)} d`;
}

export default function NotificationsPage() {
  const { data: invitations, isLoading: loadingInvitations } = useInvitations();
  const { data: notifications, isLoading: loadingNotifications } = useNotifications();
  const acceptInvitation = useAcceptInvitation();
  const rejectInvitation = useRejectInvitation();
  const markAllRead = useMarkAllRead();
  const { show } = useToast();

  const isLoading = loadingInvitations || loadingNotifications;
  const isEmpty = (invitations?.length ?? 0) === 0 && (notifications?.length ?? 0) === 0;

  return (
    <div className="mx-auto max-w-2xl px-4 pt-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Notificaciones</h1>
        {notifications && notifications.some((n) => !n.is_read) && (
          <button onClick={() => markAllRead.mutate()} className="text-sm font-medium text-brand-600">
            Marcar todas
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : isEmpty ? (
        <EmptyState icon="🔔" title="Sin notificaciones" description="Aquí verás invitaciones y actividad de tus listas" />
      ) : (
        <div className="space-y-3">
          {invitations?.map((invitation) => (
            <div
              key={invitation.id}
              className="rounded-2xl border border-brand-100 bg-brand-50 p-4 dark:border-neutral-800 dark:bg-neutral-900"
            >
              <p className="text-sm">
                <span className="font-medium">{invitation.sender?.name || "Alguien"}</span> compartió contigo:
              </p>
              <p className="mt-0.5 font-semibold">&ldquo;{invitation.list_name ?? "una lista"}&rdquo;</p>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={async () => {
                    try {
                      await acceptInvitation.mutateAsync(invitation.id);
                      show("Invitación aceptada", "success");
                    } catch {
                      show("No se pudo aceptar la invitación", "error");
                    }
                  }}
                  className="tap-target flex-1 rounded-xl bg-brand-600 text-sm font-medium text-white"
                >
                  Aceptar
                </button>
                <button
                  onClick={() => rejectInvitation.mutate(invitation.id)}
                  className="tap-target flex-1 rounded-xl border border-neutral-300 text-sm font-medium text-neutral-600 dark:border-neutral-700"
                >
                  Rechazar
                </button>
              </div>
            </div>
          ))}

          {notifications?.map((notification) => (
            <div
              key={notification.id}
              className={
                "rounded-2xl border p-4 " +
                (notification.is_read
                  ? "border-neutral-100 dark:border-neutral-800"
                  : "border-brand-200 bg-white dark:bg-neutral-900")
              }
            >
              <p className="font-medium">{notification.title}</p>
              <p className="text-sm text-neutral-500">{notification.message}</p>
              <p className="mt-1 text-xs text-neutral-400">{timeAgo(notification.created_at)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
