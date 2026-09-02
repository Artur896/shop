"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { listsApi } from "@/features/lists/api";
import { useItems, useDeleteItem, useToggleItem } from "@/features/lists/itemHooks";
import { ItemRow } from "@/features/lists/ItemRow";
import { AddItemModal } from "@/features/lists/AddItemModal";
import { ShareListModal } from "@/features/lists/ShareListModal";
import { useListSocket } from "@/features/realtime/useListSocket";
import { ProgressBar } from "@/components/ProgressBar";
import { EmptyState } from "@/components/EmptyState";
import { Skeleton } from "@/components/Skeleton";
import { CATEGORY_LABELS } from "@/types";

export default function ListDetailPage() {
  const params = useParams<{ id: string }>();
  const listId = params.id;
  const [addOpen, setAddOpen] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  const { data: list } = useQuery({ queryKey: ["lists", listId], queryFn: () => listsApi.getList(listId) });
  const { data: items, isLoading } = useItems(listId);
  const toggleItem = useToggleItem(listId);
  const deleteItem = useDeleteItem(listId);
  useListSocket(listId);

  const canEdit = list?.my_role === "owner" || list?.my_role === "editor";
  const canShare = list?.my_role === "owner";

  const { pending, completed, byCategory } = useMemo(() => {
    const all = items ?? [];
    const pending = all.filter((i) => !i.is_completed);
    const completed = all.filter((i) => i.is_completed);
    const byCategory = new Map<string, typeof pending>();
    for (const item of pending) {
      const key = item.category || "otros";
      byCategory.set(key, [...(byCategory.get(key) ?? []), item]);
    }
    return { pending, completed, byCategory };
  }, [items]);

  const total = (items ?? []).length;
  const percent = total > 0 ? Math.round((completed.length / total) * 100) : 0;

  return (
    <div className="mx-auto max-w-2xl pb-6">
      <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-neutral-200 bg-white/95 px-4 py-3 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/95">
        <Link href="/dashboard" aria-label="Volver" className="tap-target flex items-center justify-center text-xl">
          ←
        </Link>
        <div className="min-w-0 flex-1">
          <h1 className="truncate font-semibold">{list?.icon ? `${list.icon} ` : ""}{list?.name ?? "Cargando…"}</h1>
          {total > 0 && (
            <p className="text-xs text-neutral-500">
              {completed.length} / {total} productos
            </p>
          )}
        </div>
        {canShare && (
          <button
            onClick={() => setShareOpen(true)}
            className="tap-target rounded-full px-3 text-sm font-medium text-brand-600"
          >
            Compartir
          </button>
        )}
      </header>

      {total > 0 && (
        <div className="px-4 pt-3">
          <ProgressBar value={percent} />
        </div>
      )}

      <div className="px-4 pt-4">
        {isLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : total === 0 ? (
          <EmptyState
            icon="📝"
            title="Lista vacía"
            description="Agrega productos manualmente o pídele a un asistente de IA que los cree por ti"
            action={
              canEdit && (
                <button
                  onClick={() => setAddOpen(true)}
                  className="tap-target rounded-full bg-brand-600 px-5 text-sm font-medium text-white"
                >
                  Agregar producto
                </button>
              )
            }
          />
        ) : (
          <div className="space-y-5">
            {[...byCategory.entries()].map(([category, categoryItems]) => (
              <div key={category}>
                <h2 className="mb-1.5 px-1 text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  {CATEGORY_LABELS[category] ?? category}
                </h2>
                <div className="divide-y divide-neutral-100 overflow-hidden rounded-2xl border border-neutral-100 dark:divide-neutral-800 dark:border-neutral-800">
                  <AnimatePresence initial={false}>
                    {categoryItems.map((item) => (
                      <motion.div key={item.id} exit={{ opacity: 0, height: 0 }} layout>
                        <ItemRow
                          item={item}
                          canEdit={canEdit}
                          onToggle={(completed) => toggleItem.mutate({ itemId: item.id, completed })}
                          onDelete={() => deleteItem.mutate(item.id)}
                        />
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            ))}

            {completed.length > 0 && (
              <div>
                <h2 className="mb-1.5 px-1 text-xs font-semibold uppercase tracking-wide text-neutral-400">
                  Comprados
                </h2>
                <div className="divide-y divide-neutral-100 overflow-hidden rounded-2xl border border-neutral-100 dark:divide-neutral-800 dark:border-neutral-800">
                  <AnimatePresence initial={false}>
                    {completed.map((item) => (
                      <motion.div key={item.id} exit={{ opacity: 0, height: 0 }} layout>
                        <ItemRow
                          item={item}
                          canEdit={canEdit}
                          onToggle={(completed) => toggleItem.mutate({ itemId: item.id, completed })}
                          onDelete={() => deleteItem.mutate(item.id)}
                        />
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {canEdit && total > 0 && (
        <button
          onClick={() => setAddOpen(true)}
          aria-label="Agregar producto"
          className="tap-target fixed bottom-24 right-5 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-2xl text-white shadow-lg active:scale-95 sm:bottom-8"
        >
          +
        </button>
      )}

      <AddItemModal listId={listId} open={addOpen} onClose={() => setAddOpen(false)} />
      {canShare && <ShareListModal listId={listId} open={shareOpen} onClose={() => setShareOpen(false)} />}
    </div>
  );
}
