import { apiFetch } from "./apiClient";
import { getPendingOperations, removePendingOperation, type PendingOperation } from "./db";

/**
 * Pending Operations Queue → Sync → API → Postgres → WebSockets → other users
 * (see product brief section 22). Each locally-created mutation is queued in
 * IndexedDB immediately (so the UI can update optimistically even offline) and
 * flushed here once the browser reports it's back online.
 */
async function applyOperation(op: PendingOperation): Promise<void> {
  switch (op.kind) {
    case "add_item":
      await apiFetch(`/lists/${op.listId}/items`, { method: "POST", body: op.payload });
      return;
    case "update_item":
      await apiFetch(`/items/${op.itemId}`, { method: "PATCH", body: op.payload });
      return;
    case "delete_item":
      await apiFetch(`/items/${op.itemId}`, { method: "DELETE" });
      return;
    case "complete_item":
      await apiFetch(`/items/${op.itemId}/complete`, { method: "POST" });
      return;
    case "uncomplete_item":
      await apiFetch(`/items/${op.itemId}/uncomplete`, { method: "POST" });
      return;
  }
}

let syncing = false;

export async function syncPendingOperations(): Promise<{ synced: number; failed: number }> {
  if (syncing || typeof window === "undefined" || !navigator.onLine) return { synced: 0, failed: 0 };
  syncing = true;
  let synced = 0;
  let failed = 0;
  try {
    const ops = await getPendingOperations();
    for (const op of ops) {
      try {
        await applyOperation(op);
        await removePendingOperation(op.id);
        synced += 1;
      } catch {
        // Leave it queued — a later sync pass (next reconnect, or the periodic
        // retry in useOfflineSync) will retry it. A 4xx here almost always means
        // the target was deleted elsewhere; we keep it simple and just retry.
        failed += 1;
      }
    }
  } finally {
    syncing = false;
  }
  return { synced, failed };
}
