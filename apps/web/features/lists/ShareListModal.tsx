"use client";

import { useState, type FormEvent } from "react";
import { Modal } from "@/components/Modal";
import { useToast } from "@/components/ToastProvider";
import { useInviteMember, useMembers, useRemoveMember } from "./membersHooks";

export function ShareListModal({ listId, open, onClose }: { listId: string; open: boolean; onClose: () => void }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"editor" | "viewer">("editor");
  const { data: members } = useMembers(listId);
  const invite = useInviteMember(listId);
  const remove = useRemoveMember(listId);
  const { show } = useToast();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!email.trim()) return;
    try {
      await invite.mutateAsync({ email: email.trim(), role });
      show("Invitación enviada", "success");
      setEmail("");
    } catch {
      show("No se pudo enviar la invitación", "error");
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Compartir lista">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Correo</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@email.com"
            className="tap-target w-full rounded-xl border border-neutral-300 px-4 py-3 text-base outline-none focus:border-brand-600 focus:ring-2 focus:ring-brand-100 dark:border-neutral-700 dark:bg-neutral-950"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Permiso</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setRole("editor")}
              className={
                "tap-target flex-1 rounded-xl border px-3 text-sm font-medium " +
                (role === "editor"
                  ? "border-brand-600 bg-brand-50 text-brand-700 dark:bg-neutral-800"
                  : "border-neutral-300 text-neutral-500 dark:border-neutral-700")
              }
            >
              Puede editar
            </button>
            <button
              type="button"
              onClick={() => setRole("viewer")}
              className={
                "tap-target flex-1 rounded-xl border px-3 text-sm font-medium " +
                (role === "viewer"
                  ? "border-brand-600 bg-brand-50 text-brand-700 dark:bg-neutral-800"
                  : "border-neutral-300 text-neutral-500 dark:border-neutral-700")
              }
            >
              Solo visualizar
            </button>
          </div>
        </div>
        <button
          type="submit"
          disabled={invite.isPending}
          className="tap-target w-full rounded-xl bg-brand-600 py-3 font-medium text-white active:scale-[0.98] disabled:opacity-60"
        >
          Compartir
        </button>
      </form>

      {members && members.length > 0 && (
        <div className="mt-5 border-t border-neutral-100 pt-4 dark:border-neutral-800">
          <h3 className="mb-2 text-sm font-medium text-neutral-500">Miembros</h3>
          <ul className="space-y-2">
            {members.map((member) => (
              <li key={member.id} className="flex items-center justify-between text-sm">
                <span>
                  {member.user?.name || member.user?.email} ·{" "}
                  <span className="text-neutral-400">{member.role}</span>
                </span>
                {member.role !== "owner" && (
                  <button
                    onClick={() => remove.mutate(member.user_id)}
                    className="tap-target px-2 text-xs font-medium text-red-500"
                  >
                    Quitar
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Modal>
  );
}
