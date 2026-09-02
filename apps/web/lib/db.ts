import { openDB, type DBSchema, type IDBPDatabase } from "idb";
import type { ListSummary, ShoppingItem } from "@/types";

export interface PendingOperation {
  id: string;
  kind: "add_item" | "update_item" | "delete_item" | "complete_item" | "uncomplete_item";
  listId: string;
  itemId?: string;
  payload?: unknown;
  createdAt: number;
}

interface ShoppingDB extends DBSchema {
  lists: { key: string; value: ListSummary };
  items: { key: string; value: ShoppingItem; indexes: { by_list: string } };
  pending_ops: { key: string; value: PendingOperation };
}

let dbPromise: Promise<IDBPDatabase<ShoppingDB>> | null = null;

function getDb() {
  if (typeof window === "undefined") {
    throw new Error("IndexedDB is only available in the browser");
  }
  if (!dbPromise) {
    dbPromise = openDB<ShoppingDB>("shopping-lists", 1, {
      upgrade(db) {
        db.createObjectStore("lists", { keyPath: "id" });
        const items = db.createObjectStore("items", { keyPath: "id" });
        items.createIndex("by_list", "list_id");
        db.createObjectStore("pending_ops", { keyPath: "id" });
      },
    });
  }
  return dbPromise;
}

export async function cacheLists(lists: ListSummary[]) {
  const db = await getDb();
  const tx = db.transaction("lists", "readwrite");
  await Promise.all(lists.map((l) => tx.store.put(l)));
  await tx.done;
}

export async function getCachedLists(): Promise<ListSummary[]> {
  const db = await getDb();
  return db.getAll("lists");
}

export async function cacheItems(listId: string, items: ShoppingItem[]) {
  const db = await getDb();
  const tx = db.transaction("items", "readwrite");
  const existing = await tx.store.index("by_list").getAllKeys(listId);
  await Promise.all(existing.map((key) => tx.store.delete(key)));
  await Promise.all(items.map((i) => tx.store.put(i)));
  await tx.done;
}

export async function getCachedItems(listId: string): Promise<ShoppingItem[]> {
  const db = await getDb();
  return db.getAllFromIndex("items", "by_list", listId);
}

export async function enqueueOperation(op: Omit<PendingOperation, "id" | "createdAt">) {
  const db = await getDb();
  const entry: PendingOperation = { ...op, id: crypto.randomUUID(), createdAt: Date.now() };
  await db.put("pending_ops", entry);
  return entry;
}

export async function getPendingOperations(): Promise<PendingOperation[]> {
  const db = await getDb();
  const all = await db.getAll("pending_ops");
  return all.sort((a, b) => a.createdAt - b.createdAt);
}

export async function removePendingOperation(id: string) {
  const db = await getDb();
  await db.delete("pending_ops", id);
}
