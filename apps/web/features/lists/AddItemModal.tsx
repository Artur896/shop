"use client";

import { useState, type FormEvent } from "react";
import { Modal } from "@/components/Modal";
import { useToast } from "@/components/ToastProvider";
import { CATEGORIES, CATEGORY_LABELS } from "@/types";
import { useAddItem } from "./itemHooks";

export function AddItemModal({ listId, open, onClose }: { listId: string; open: boolean; onClose: () => void }) {
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unit, setUnit] = useState("");
  const [category, setCategory] = useState("otros");
  const addItem = useAddItem(listId);
  const { show } = useToast();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      await addItem.mutateAsync({
        name: name.trim(),
        quantity: Number(quantity) || 1,
        unit: unit.trim() || undefined,
        category,
      });
      setName("");
      setQuantity("1");
      setUnit("");
      onClose();
    } catch {
      show("No se pudo agregar el producto", "error");
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Agregar producto">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Nombre</label>
          <input
            autoFocus
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Leche"
            className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
          />
        </div>
        <div className="flex gap-3">
          <div className="w-24">
            <label className="mb-1 block text-sm font-medium">Cantidad</label>
            <input
              type="number"
              min="0"
              step="0.5"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="tap-target w-full rounded-xl border border-neutral-300 px-3 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
            />
          </div>
          <div className="flex-1">
            <label className="mb-1 block text-sm font-medium">Unidad (opcional)</label>
            <input
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              placeholder="litros, kg, pza..."
              className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Categoría</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {CATEGORY_LABELS[cat]}
              </option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          disabled={addItem.isPending}
          className="tap-target w-full rounded-xl bg-brand-600 py-3 font-medium text-white active:scale-[0.98] disabled:opacity-60"
        >
          Agregar
        </button>
      </form>
    </Modal>
  );
}
