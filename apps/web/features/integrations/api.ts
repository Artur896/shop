import { apiFetch } from "@/lib/apiClient";
import type { AIProvider, Integration } from "@/types";

export const integrationsApi = {
  list: () => apiFetch<Integration[]>("/integrations"),
  connect: (provider: AIProvider, scopes: string[]) =>
    apiFetch<{ integration: Integration; token: string; scopes: string[] }>(
      `/integrations/${provider}/connect`,
      { method: "POST", body: { scopes } }
    ),
  disconnect: (provider: AIProvider) => apiFetch<void>(`/integrations/${provider}`, { method: "DELETE" }),
  updatePermissions: (provider: AIProvider, scopes: string[]) =>
    apiFetch<Integration>(`/integrations/${provider}/permissions`, { method: "PATCH", body: { scopes } }),
};
