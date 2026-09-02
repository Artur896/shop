import { apiFetch } from "@/lib/apiClient";
import type { Invitation, ListSummary, Member, ShoppingItem } from "@/types";

export interface CreateListInput {
  name: string;
  description?: string;
  icon?: string;
}

export interface CreateItemInput {
  name: string;
  quantity?: number;
  unit?: string;
  category?: string;
  notes?: string;
  estimated_price?: number;
}

export type UpdateItemInput = Partial<CreateItemInput> & { is_completed?: boolean };

export const listsApi = {
  getLists: () => apiFetch<{ mine: ListSummary[]; shared: ListSummary[] }>("/lists"),
  getList: (id: string) => apiFetch<ListSummary>(`/lists/${id}`),
  createList: (input: CreateListInput) => apiFetch<ListSummary>("/lists", { method: "POST", body: input }),
  updateList: (id: string, input: Partial<CreateListInput>) =>
    apiFetch<ListSummary>(`/lists/${id}`, { method: "PATCH", body: input }),
  deleteList: (id: string) => apiFetch<void>(`/lists/${id}`, { method: "DELETE" }),

  getItems: (listId: string) => apiFetch<ShoppingItem[]>(`/lists/${listId}/items`),
  addItem: (listId: string, input: CreateItemInput) =>
    apiFetch<ShoppingItem>(`/lists/${listId}/items`, { method: "POST", body: input }),
  updateItem: (itemId: string, input: UpdateItemInput) =>
    apiFetch<ShoppingItem>(`/items/${itemId}`, { method: "PATCH", body: input }),
  deleteItem: (itemId: string) => apiFetch<void>(`/items/${itemId}`, { method: "DELETE" }),
  completeItem: (itemId: string) => apiFetch<ShoppingItem>(`/items/${itemId}/complete`, { method: "POST" }),
  uncompleteItem: (itemId: string) => apiFetch<ShoppingItem>(`/items/${itemId}/uncomplete`, { method: "POST" }),

  getMembers: (listId: string) => apiFetch<Member[]>(`/lists/${listId}/members`),
  inviteMember: (listId: string, email: string, role: "editor" | "viewer") =>
    apiFetch<Invitation>(`/lists/${listId}/members`, { method: "POST", body: { email, role } }),
  removeMember: (listId: string, userId: string) =>
    apiFetch<void>(`/lists/${listId}/members/${userId}`, { method: "DELETE" }),
};
