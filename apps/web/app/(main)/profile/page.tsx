"use client";

import Link from "next/link";
import { useAuth } from "@/features/auth/AuthContext";

export default function ProfilePage() {
  const { user, logout } = useAuth();

  return (
    <div className="mx-auto max-w-2xl px-4 pt-6">
      <h1 className="mb-6 text-2xl font-semibold">Perfil</h1>

      <div className="mb-6 flex items-center gap-4 rounded-2xl border border-neutral-200 p-4 dark:border-neutral-800">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-xl font-medium text-white">
          {user?.name?.[0]?.toUpperCase() ?? "?"}
        </div>
        <div>
          <p className="font-medium">{user?.name}</p>
          <p className="text-sm text-neutral-500">{user?.email}</p>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-neutral-200 dark:border-neutral-800">
        <Link
          href="/profile/integrations"
          className="flex items-center justify-between px-4 py-3.5 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-900"
        >
          <span className="flex items-center gap-2">🤖 Integraciones · Asistentes de IA</span>
          <span className="text-neutral-400">›</span>
        </Link>
      </div>

      <button
        onClick={logout}
        className="tap-target mt-6 w-full rounded-xl border border-red-200 py-3 font-medium text-red-600 dark:border-red-900/50"
      >
        Cerrar sesión
      </button>
    </div>
  );
}
