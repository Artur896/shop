"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/apiClient";
import { useAuth } from "@/features/auth/AuthContext";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Inicio", icon: "🏠" },
  { href: "/notifications", label: "Notificaciones", icon: "🔔" },
  { href: "/profile", label: "Perfil", icon: "👤" },
];

function useUnreadCount() {
  const { user } = useAuth();
  const { data } = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: () => apiFetch<{ count: number }>("/notifications/unread-count"),
    enabled: !!user,
    refetchInterval: 30_000,
  });
  return data?.count ?? 0;
}

export function BottomNav() {
  const pathname = usePathname();
  const unread = useUnreadCount();

  return (
    <nav className="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-neutral-200 bg-white/95 backdrop-blur sm:hidden dark:border-neutral-800 dark:bg-neutral-950/95">
      <ul className="grid grid-cols-3">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={
                  "tap-target relative flex flex-col items-center justify-center gap-0.5 py-2 text-xs font-medium " +
                  (active ? "text-brand-600" : "text-neutral-500")
                }
              >
                <span className="text-lg leading-none">{item.icon}</span>
                {item.label}
                {item.href === "/notifications" && unread > 0 && (
                  <span className="absolute right-[28%] top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] text-white">
                    {unread > 9 ? "9+" : unread}
                  </span>
                )}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const unread = useUnreadCount();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-60 flex-col border-r border-neutral-200 bg-white p-4 sm:flex dark:border-neutral-800 dark:bg-neutral-950">
      <div className="mb-8 flex items-center gap-2 px-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white">🛒</div>
        <span className="font-semibold">Listas</span>
      </div>
      <ul className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={
                  "relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition " +
                  (active
                    ? "bg-brand-50 text-brand-700 dark:bg-neutral-900 dark:text-brand-500"
                    : "text-neutral-600 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-900")
                }
              >
                <span>{item.icon}</span>
                {item.label}
                {item.href === "/notifications" && unread > 0 && (
                  <span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] text-white">
                    {unread > 9 ? "9+" : unread}
                  </span>
                )}
              </Link>
            </li>
          );
        })}
      </ul>
      {user && (
        <button
          onClick={logout}
          className="mt-4 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-900"
        >
          Cerrar sesión
        </button>
      )}
    </aside>
  );
}
