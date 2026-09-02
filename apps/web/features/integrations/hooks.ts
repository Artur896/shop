"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AIProvider } from "@/types";
import { integrationsApi } from "./api";

export function useIntegrations() {
  return useQuery({ queryKey: ["integrations"], queryFn: integrationsApi.list });
}

export function useConnectIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ provider, scopes }: { provider: AIProvider; scopes: string[] }) =>
      integrationsApi.connect(provider, scopes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["integrations"] }),
  });
}

export function useDisconnectIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (provider: AIProvider) => integrationsApi.disconnect(provider),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["integrations"] }),
  });
}

export function useUpdatePermissions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ provider, scopes }: { provider: AIProvider; scopes: string[] }) =>
      integrationsApi.updatePermissions(provider, scopes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["integrations"] }),
  });
}
