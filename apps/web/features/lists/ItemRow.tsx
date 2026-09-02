"use client";

import { motion, useAnimation, type PanInfo } from "framer-motion";
import { useState } from "react";
import type { ShoppingItem } from "@/types";

const SWIPE_THRESHOLD = -80;

export function ItemRow({
  item,
  canEdit,
  onToggle,
  onDelete,
}: {
  item: ShoppingItem;
  canEdit: boolean;
  onToggle: (completed: boolean) => void;
  onDelete: () => void;
}) {
  const controls = useAnimation();
  const [revealed, setRevealed] = useState(false);

  const onDragEnd = (_e: PointerEvent | MouseEvent | TouchEvent, info: PanInfo) => {
    if (!canEdit) return;
    if (info.offset.x < SWIPE_THRESHOLD) {
      controls.start({ x: -88 });
      setRevealed(true);
    } else {
      controls.start({ x: 0 });
      setRevealed(false);
    }
  };

  const quantityLabel = [item.quantity, item.unit].filter(Boolean).join(" ");

  return (
    <div className="relative overflow-hidden">
      {canEdit && (
        <button
          onClick={() => {
            onDelete();
            controls.start({ x: 0 });
          }}
          aria-label={`Eliminar ${item.name}`}
          className="tap-target absolute inset-y-0 right-0 flex w-20 items-center justify-center bg-red-500 text-sm font-medium text-white"
        >
          Eliminar
        </button>
      )}
      <motion.div
        drag={canEdit ? "x" : false}
        dragConstraints={{ left: -88, right: 0 }}
        dragElastic={0.05}
        animate={controls}
        onDragEnd={onDragEnd}
        onClick={() => revealed && (controls.start({ x: 0 }), setRevealed(false))}
        className="relative z-10 flex items-center gap-3 bg-white px-4 py-3 dark:bg-neutral-900"
      >
        <button
          onClick={() => canEdit && onToggle(!item.is_completed)}
          disabled={!canEdit}
          aria-pressed={item.is_completed}
          aria-label={item.is_completed ? `Marcar ${item.name} como pendiente` : `Marcar ${item.name} como comprado`}
          className={
            "tap-target flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 text-sm transition " +
            (item.is_completed
              ? "border-brand-500 bg-brand-500 text-white"
              : "border-neutral-300 dark:border-neutral-700")
          }
        >
          {item.is_completed && "✓"}
        </button>
        <div className="min-w-0 flex-1">
          <p className={"truncate font-medium " + (item.is_completed ? "text-neutral-400 line-through" : "")}>
            {item.name}
          </p>
          {(quantityLabel || item.notes) && (
            <p className="truncate text-sm text-neutral-500">
              {quantityLabel}
              {quantityLabel && item.notes ? " · " : ""}
              {item.notes}
            </p>
          )}
        </div>
        {item.estimated_price && (
          <span className="shrink-0 text-sm text-neutral-500">${item.estimated_price}</span>
        )}
      </motion.div>
    </div>
  );
}
