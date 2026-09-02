"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listsApi } from "./api";

export function useMembers(listId: string) {
  return useQuery({
    queryKey: ["members", listId],
    queryFn: () => listsApi.getMembers(listId),
  });
}

export function useInviteMember(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: "editor" | "viewer" }) =>
      listsApi.inviteMember(listId, email, role),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["members", listId] }),
  });
}

export function useRemoveMember(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => listsApi.removeMember(listId, userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["members", listId] }),
  });
}
