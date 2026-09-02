"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cacheLists, getCachedLists } from "@/lib/db";
import type { ListSummary } from "@/types";
import { listsApi, type CreateListInput } from "./api";

export function useLists() {
  return useQuery({
    queryKey: ["lists"],
    queryFn: async () => {
      try {
        const data = await listsApi.getLists();
        await cacheLists([...data.mine, ...data.shared]);
        return data;
      } catch (err) {
        if (typeof navigator !== "undefined" && !navigator.onLine) {
          const cached = await getCachedLists();
          return { mine: cached, shared: [] as ListSummary[] };
        }
        throw err;
      }
    },
  });
}

export function useCreateList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateListInput) => listsApi.createList(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lists"] });
    },
  });
}

export function useDeleteList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => listsApi.deleteList(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lists"] });
    },
  });
}
