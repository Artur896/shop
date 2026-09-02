"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cacheItems, enqueueOperation, getCachedItems } from "@/lib/db";
import type { ShoppingItem } from "@/types";
import { listsApi, type CreateItemInput, type UpdateItemInput } from "./api";

export function useItems(listId: string) {
  return useQuery({
    queryKey: ["items", listId],
    queryFn: async () => {
      try {
        const items = await listsApi.getItems(listId);
        await cacheItems(listId, items);
        return items;
      } catch (err) {
        if (typeof navigator !== "undefined" && !navigator.onLine) {
          return getCachedItems(listId);
        }
        throw err;
      }
    },
  });
}

function makeOptimisticItem(listId: string, input: CreateItemInput): ShoppingItem {
  const now = new Date().toISOString();
  return {
    id: `temp-${crypto.randomUUID()}`,
    list_id: listId,
    name: input.name,
    quantity: input.quantity ?? 1,
    unit: input.unit ?? null,
    category: input.category ?? "otros",
    notes: input.notes ?? null,
    estimated_price: input.estimated_price ?? null,
    is_completed: false,
    version: 1,
    created_at: now,
    updated_at: now,
  };
}

function afterMutationSettle(queryClient: ReturnType<typeof useQueryClient>, listId: string) {
  if (typeof navigator !== "undefined" && navigator.onLine) {
    queryClient.invalidateQueries({ queryKey: ["items", listId] });
    queryClient.invalidateQueries({ queryKey: ["lists", listId] });
    queryClient.invalidateQueries({ queryKey: ["lists"] });
  }
}

export function useAddItem(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateItemInput) => {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        await enqueueOperation({ kind: "add_item", listId, payload: input });
        return makeOptimisticItem(listId, input);
      }
      return listsApi.addItem(listId, input);
    },
    onMutate: async (input) => {
      await queryClient.cancelQueries({ queryKey: ["items", listId] });
      const previous = queryClient.getQueryData<ShoppingItem[]>(["items", listId]);
      const optimistic = makeOptimisticItem(listId, input);
      queryClient.setQueryData<ShoppingItem[]>(["items", listId], (prev) => [...(prev ?? []), optimistic]);
      return { previous };
    },
    onError: (_err, _input, context) => {
      queryClient.setQueryData(["items", listId], context?.previous);
    },
    onSettled: () => afterMutationSettle(queryClient, listId),
  });
}

export function useUpdateItem(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ itemId, input }: { itemId: string; input: UpdateItemInput }) => {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        await enqueueOperation({ kind: "update_item", listId, itemId, payload: input });
        return null;
      }
      return listsApi.updateItem(itemId, input);
    },
    onMutate: async ({ itemId, input }) => {
      await queryClient.cancelQueries({ queryKey: ["items", listId] });
      const previous = queryClient.getQueryData<ShoppingItem[]>(["items", listId]);
      queryClient.setQueryData<ShoppingItem[]>(["items", listId], (prev) =>
        prev?.map((item) => (item.id === itemId ? { ...item, ...input } : item))
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      queryClient.setQueryData(["items", listId], context?.previous);
    },
    onSettled: () => afterMutationSettle(queryClient, listId),
  });
}

export function useToggleItem(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ itemId, completed }: { itemId: string; completed: boolean }) => {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        await enqueueOperation({ kind: completed ? "complete_item" : "uncomplete_item", listId, itemId });
        return null;
      }
      return completed ? listsApi.completeItem(itemId) : listsApi.uncompleteItem(itemId);
    },
    onMutate: async ({ itemId, completed }) => {
      await queryClient.cancelQueries({ queryKey: ["items", listId] });
      const previous = queryClient.getQueryData<ShoppingItem[]>(["items", listId]);
      queryClient.setQueryData<ShoppingItem[]>(["items", listId], (prev) =>
        prev?.map((item) => (item.id === itemId ? { ...item, is_completed: completed } : item))
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      queryClient.setQueryData(["items", listId], context?.previous);
    },
    onSettled: () => afterMutationSettle(queryClient, listId),
  });
}

export function useDeleteItem(listId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (itemId: string) => {
      if (typeof navigator !== "undefined" && !navigator.onLine) {
        await enqueueOperation({ kind: "delete_item", listId, itemId });
        return null;
      }
      return listsApi.deleteItem(itemId);
    },
    onMutate: async (itemId) => {
      await queryClient.cancelQueries({ queryKey: ["items", listId] });
      const previous = queryClient.getQueryData<ShoppingItem[]>(["items", listId]);
      queryClient.setQueryData<ShoppingItem[]>(["items", listId], (prev) =>
        prev?.filter((item) => item.id !== itemId)
      );
      return { previous };
    },
    onError: (_err, _itemId, context) => {
      queryClient.setQueryData(["items", listId], context?.previous);
    },
    onSettled: () => afterMutationSettle(queryClient, listId),
  });
}
