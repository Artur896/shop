"use client";

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { syncPendingOperations } from "@/lib/offlineQueue";
import { useToast } from "@/components/ToastProvider";

export function useOfflineSync() {
  const queryClient = useQueryClient();
  const { show } = useToast();

  useEffect(() => {
    const runSync = async () => {
      const { synced } = await syncPendingOperations();
      if (synced > 0) {
        show(`${synced} cambio${synced > 1 ? "s" : ""} sincronizado${synced > 1 ? "s" : ""}`, "success");
        queryClient.invalidateQueries();
      }
    };

    runSync();
    window.addEventListener("online", runSync);
    const interval = setInterval(runSync, 60_000);
    return () => {
      window.removeEventListener("online", runSync);
      clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
