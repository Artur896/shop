"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/Modal";
import { useToast } from "@/components/ToastProvider";
import { useCreateList } from "./hooks";

const ICONS = ["🛒", "🏠", "🎉", "🥩", "🥗", "🧹"];

export function CreateListModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [icon, setIcon] = useState(ICONS[0]);
  const createList = useCreateList();
  const { show } = useToast();
  const router = useRouter();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      const list = await createList.mutateAsync({ name: name.trim(), description: description.trim() || undefined, icon });
      setName("");
      setDescription("");
      onClose();
      router.push(`/lists/${list.id}`);
    } catch {
      show("No se pudo crear la lista", "error");
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Nueva lista">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="flex gap-2">
          {ICONS.map((option) => (
            <button
              type="button"
              key={option}
              onClick={() => setIcon(option)}
              className={
                "tap-target flex items-center justify-center rounded-xl text-xl transition " +
                (icon === option ? "bg-brand-100 ring-2 ring-brand-500 dark:bg-neutral-800" : "bg-neutral-100 dark:bg-neutral-800")
              }
            >
              {option}
            </button>
          ))}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Nombre</label>
          <input
            autoFocus
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Supermercado"
            className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Descripción (opcional)</label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Compra semanal"
            className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
          />
        </div>
        <button
          type="submit"
          disabled={createList.isPending}
          className="tap-target w-full rounded-xl bg-brand-600 py-3 font-medium text-white active:scale-[0.98] disabled:opacity-60"
        >
          {createList.isPending ? "Creando..." : "Crear lista"}
        </button>
      </form>
    </Modal>
  );
}
