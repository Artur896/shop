"use client";

import { useState } from "react";
import { Modal } from "@/components/Modal";
import { useToast } from "@/components/ToastProvider";
import { ALL_AI_SCOPES, SCOPE_LABELS, type AIProvider } from "@/types";
import { useConnectIntegration } from "./hooks";

const DEFAULT_SCOPES = ["lists:read", "lists:create", "items:read", "items:create", "items:update"];
const DESTRUCTIVE = new Set(["lists:delete", "items:delete"]);

const PROVIDER_LABELS: Record<AIProvider, string> = {
  chatgpt: "ChatGPT",
  claude: "Claude",
  gemini: "Gemini",
};

export function ConnectIntegrationModal({
  provider,
  open,
  onClose,
}: {
  provider: AIProvider | null;
  open: boolean;
  onClose: () => void;
}) {
  const [scopes, setScopes] = useState<Set<string>>(new Set(DEFAULT_SCOPES));
  const [issuedToken, setIssuedToken] = useState<string | null>(null);
  const connect = useConnectIntegration();
  const { show } = useToast();

  const toggle = (scope: string) => {
    setScopes((prev) => {
      const next = new Set(prev);
      next.has(scope) ? next.delete(scope) : next.add(scope);
      return next;
    });
  };

  const handleClose = () => {
    setIssuedToken(null);
    setScopes(new Set(DEFAULT_SCOPES));
    onClose();
  };

  const onConnect = async () => {
    if (!provider) return;
    try {
      const result = await connect.mutateAsync({ provider, scopes: [...scopes] });
      setIssuedToken(result.token);
    } catch {
      show("No se pudo conectar la integración", "error");
    }
  };

  return (
    <Modal open={open} onClose={handleClose} title={provider ? `Conectar ${PROVIDER_LABELS[provider]}` : "Conectar"}>
      {issuedToken ? (
        <div className="space-y-3">
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Copia este token y pégalo en la configuración del conector MCP de{" "}
            {provider && PROVIDER_LABELS[provider]}. Por seguridad, solo se muestra una vez.
          </p>
          <code className="block break-all rounded-xl bg-neutral-100 p-3 text-xs dark:bg-neutral-800">
            {issuedToken}
          </code>
          <button
            onClick={() => {
              navigator.clipboard?.writeText(issuedToken);
              show("Token copiado", "success");
            }}
            className="tap-target w-full rounded-xl bg-brand-600 py-3 font-medium text-white"
          >
            Copiar token
          </button>
          <button onClick={handleClose} className="tap-target w-full text-sm text-neutral-500">
            Listo
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Elige qué puede hacer {provider && PROVIDER_LABELS[provider]} en tu cuenta. Puedes cambiar esto
            después.
          </p>
          <div className="space-y-2">
            {ALL_AI_SCOPES.map((scope) => (
              <label
                key={scope}
                className="flex items-center justify-between rounded-xl border border-neutral-200 px-3 py-2.5 text-sm dark:border-neutral-800"
              >
                <span>
                  {SCOPE_LABELS[scope]}
                  {DESTRUCTIVE.has(scope) && (
                    <span className="ml-1.5 rounded-full bg-red-50 px-1.5 py-0.5 text-[10px] font-medium text-red-600 dark:bg-red-950">
                      sensible
                    </span>
                  )}
                </span>
                <input
                  type="checkbox"
                  checked={scopes.has(scope)}
                  onChange={() => toggle(scope)}
                  className="h-5 w-5 accent-brand-600"
                />
              </label>
            ))}
          </div>
          <button
            onClick={onConnect}
            disabled={connect.isPending}
            className="tap-target w-full rounded-xl bg-brand-600 py-3 font-medium text-white disabled:opacity-60"
          >
            Conectar
          </button>
        </div>
      )}
    </Modal>
  );
}
