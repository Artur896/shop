"use client";

import { useState } from "react";
import Link from "next/link";
import { useToast } from "@/components/ToastProvider";
import { Skeleton } from "@/components/Skeleton";
import { ConnectIntegrationModal } from "@/features/integrations/ConnectIntegrationModal";
import { useDisconnectIntegration, useIntegrations } from "@/features/integrations/hooks";
import { SCOPE_LABELS, type AIProvider } from "@/types";

const PROVIDER_META: Record<AIProvider, { label: string; icon: string }> = {
  chatgpt: { label: "ChatGPT", icon: "💬" },
  claude: { label: "Claude", icon: "✳️" },
  gemini: { label: "Gemini", icon: "✨" },
};

export default function IntegrationsPage() {
  const { data: integrations, isLoading } = useIntegrations();
  const disconnect = useDisconnectIntegration();
  const [connecting, setConnecting] = useState<AIProvider | null>(null);
  const { show } = useToast();

  return (
    <div className="mx-auto max-w-2xl px-4 pt-6">
      <div className="mb-1 flex items-center gap-2">
        <Link href="/profile" aria-label="Volver" className="tap-target text-xl">
          ←
        </Link>
        <h1 className="text-2xl font-semibold">Asistentes de IA</h1>
      </div>
      <p className="mb-6 px-1 text-sm text-neutral-500">
        Conecta un asistente para crear y modificar listas usando lenguaje natural, con los permisos que tú
        decidas.
      </p>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {integrations?.map((integration) => {
            const meta = PROVIDER_META[integration.provider];
            const connected = integration.status === "connected";
            return (
              <div
                key={integration.provider}
                className="rounded-2xl border border-neutral-200 p-4 dark:border-neutral-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{meta.icon}</span>
                    <div>
                      <p className="font-medium">{meta.label}</p>
                      <p className={"text-xs " + (connected ? "text-brand-600" : "text-neutral-400")}>
                        {connected ? "Conectado" : "No conectado"}
                      </p>
                    </div>
                  </div>
                  {connected ? (
                    <button
                      onClick={async () => {
                        await disconnect.mutateAsync(integration.provider);
                        show(`${meta.label} desconectado`, "default");
                      }}
                      className="tap-target rounded-full border border-neutral-300 px-3 text-sm font-medium text-neutral-600 dark:border-neutral-700"
                    >
                      Desconectar
                    </button>
                  ) : (
                    <button
                      onClick={() => setConnecting(integration.provider)}
                      className="tap-target rounded-full bg-brand-600 px-4 text-sm font-medium text-white"
                    >
                      Conectar
                    </button>
                  )}
                </div>
                {connected && integration.granted_scopes.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {integration.granted_scopes.map((scope) => (
                      <span
                        key={scope}
                        className="rounded-full bg-neutral-100 px-2 py-0.5 text-[11px] text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400"
                      >
                        {SCOPE_LABELS[scope] ?? scope}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <ConnectIntegrationModal provider={connecting} open={!!connecting} onClose={() => setConnecting(null)} />
    </div>
  );
}
