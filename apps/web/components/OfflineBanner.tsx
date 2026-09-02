"use client";

import { useOnlineStatus } from "@/hooks/useOnlineStatus";

export function OfflineBanner() {
  const online = useOnlineStatus();
  if (online) return null;

  return (
    <div className="sticky top-0 z-30 bg-amber-500 px-4 py-1.5 text-center text-xs font-medium text-white">
      Sin conexión — tus cambios se guardarán y sincronizarán al reconectar
    </div>
  );
}
