"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ProgressBar } from "@/components/ProgressBar";
import type { ListSummary } from "@/types";

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const minutes = Math.round(diffMs / 60_000);
  if (minutes < 1) return "justo ahora";
  if (minutes < 60) return `hace ${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `hace ${hours} h`;
  const days = Math.round(hours / 24);
  return `hace ${days} d`;
}

export function ListCard({ list }: { list: ListSummary }) {
  const total = list.total_items;
  const completed = list.completed_items;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
    >
      <Link
        href={`/lists/${list.id}`}
        className="block rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm transition hover:border-brand-200 dark:border-neutral-800 dark:bg-neutral-900"
      >
        <div className="mb-2 flex items-center justify-between">
          <h3 className="truncate font-medium">{list.icon ? `${list.icon} ` : ""}{list.name}</h3>
          {list.my_role !== "owner" && (
            <span className="shrink-0 rounded-full bg-neutral-100 px-2 py-0.5 text-[11px] font-medium text-neutral-500 dark:bg-neutral-800">
              {list.my_role === "editor" ? "Editor" : "Solo lectura"}
            </span>
          )}
        </div>
        <ProgressBar value={percent} />
        <div className="mt-2 flex items-center justify-between text-xs text-neutral-500">
          <span>
            {completed} / {total} productos
          </span>
          <span>Actualizada {timeAgo(list.updated_at)}</span>
        </div>
      </Link>
    </motion.div>
  );
}
