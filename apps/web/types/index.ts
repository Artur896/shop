export type ListRole = "owner" | "editor" | "viewer";

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string | null;
}

export interface ListSummary {
  id: string;
  name: string;
  description?: string | null;
  icon?: string | null;
  owner_id: string;
  version: number;
  created_at: string;
  updated_at: string;
  total_items: number;
  completed_items: number;
  my_role: ListRole;
}

export interface ShoppingItem {
  id: string;
  list_id: string;
  name: string;
  quantity: string | number;
  unit?: string | null;
  category: string;
  notes?: string | null;
  estimated_price?: string | number | null;
  is_completed: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Member {
  id: string;
  list_id: string;
  user_id: string;
  role: ListRole;
  status: "active" | "removed";
  created_at: string;
  user?: User | null;
}

export type InvitationStatus = "pending" | "accepted" | "rejected" | "expired";

export interface Invitation {
  id: string;
  list_id: string;
  list_name?: string | null;
  sender?: User | null;
  receiver_id: string;
  role: ListRole;
  status: InvitationStatus;
  expires_at: string;
  created_at: string;
}

export type NotificationType =
  | "LIST_INVITATION"
  | "INVITATION_ACCEPTED"
  | "LIST_SHARED"
  | "MEMBER_ADDED"
  | "MEMBER_REMOVED"
  | "ITEM_ADDED"
  | "ITEM_COMPLETED";

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, unknown> | null;
  is_read: boolean;
  created_at: string;
}

export type AIProvider = "chatgpt" | "claude" | "gemini";

export interface Integration {
  id: string;
  provider: AIProvider;
  status: "connected" | "disconnected";
  granted_scopes: string[];
  updated_at: string;
}

export const CATEGORIES = [
  "frutas_verduras",
  "lacteos",
  "carnes",
  "bebidas",
  "limpieza",
  "higiene",
  "despensa",
  "otros",
] as const;

export const CATEGORY_LABELS: Record<string, string> = {
  frutas_verduras: "Frutas y verduras",
  lacteos: "Lácteos",
  carnes: "Carnes",
  bebidas: "Bebidas",
  limpieza: "Limpieza",
  higiene: "Higiene",
  despensa: "Despensa",
  otros: "Otros",
};

export const ALL_AI_SCOPES = [
  "lists:read",
  "lists:create",
  "lists:update",
  "lists:delete",
  "items:read",
  "items:create",
  "items:update",
  "items:delete",
  "members:read",
  "members:invite",
] as const;

export const SCOPE_LABELS: Record<string, string> = {
  "lists:read": "Ver mis listas",
  "lists:create": "Crear listas",
  "lists:update": "Modificar listas",
  "lists:delete": "Eliminar listas",
  "items:read": "Ver productos",
  "items:create": "Agregar productos",
  "items:update": "Modificar productos",
  "items:delete": "Eliminar productos",
  "members:read": "Ver miembros",
  "members:invite": "Compartir listas con otros usuarios",
};
