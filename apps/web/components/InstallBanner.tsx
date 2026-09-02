"use client";

import { useState } from "react";
import { useInstallPrompt } from "@/hooks/useInstallPrompt";

export function InstallBanner() {
  const { canInstall, promptInstall } = useInstallPrompt();
  const [dismissed, setDismissed] = useState(false);
  const [explaining, setExplaining] = useState(false);

  if (!canInstall || dismissed) return null;

  return (
    <div className="mx-4 mt-3 rounded-2xl border border-brand-100 bg-brand-50 p-4 text-sm dark:border-neutral-800 dark:bg-neutral-900">
      {!explaining ? (
        <div className="flex items-center justify-between gap-3">
          <p className="text-neutral-700 dark:text-neutral-300">
            Instala la app para acceso rápido y uso sin conexión.
          </p>
          <div className="flex shrink-0 gap-2">
            <button
              onClick={() => setDismissed(true)}
              className="tap-target rounded-lg px-2 text-neutral-500"
            >
              Ahora no
            </button>
            <button
              onClick={() => setExplaining(true)}
              className="tap-target rounded-lg bg-brand-600 px-3 font-medium text-white"
            >
              Instalar
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-neutral-700 dark:text-neutral-300">
            Al instalar podrás abrir tus listas como una app, incluso sin conexión, y
            recibir notificaciones de invitaciones y cambios compartidos.
          </p>
          <div className="flex justify-end gap-2">
            <button onClick={() => setDismissed(true)} className="tap-target rounded-lg px-2 text-neutral-500">
              Cancelar
            </button>
            <button
              onClick={() => promptInstall().then(() => setDismissed(true))}
              className="tap-target rounded-lg bg-brand-600 px-3 font-medium text-white"
            >
              Continuar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
