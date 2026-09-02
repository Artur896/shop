"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { tokenStore } from "@/lib/tokenStore";
import type { ShoppingItem } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type ListEvent =
  | { type: "CONNECTED"; list_id: string; role: string }
  | { type: "ITEM_CREATED" | "ITEM_UPDATED" | "ITEM_COMPLETED" | "ITEM_UNCOMPLETED"; data: ShoppingItem }
  | { type: "ITEM_DELETED"; data: { id: string } }
  | { type: "MEMBER_ADDED" | "MEMBER_REMOVED"; data: Record<string, unknown> }
  | { type: "PONG" };

/**
 * One WebSocket connection per open list (section 16). Applies incoming events
 * directly onto the TanStack Query cache for that list's items — no full-list
 * refetch, just the row that actually changed.
 */
export function useListSocket(listId: string | undefined) {
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const shouldReconnect = useRef(true);

  useEffect(() => {
    if (!listId) return;
    shouldReconnect.current = true;

    let heartbeat: ReturnType<typeof setInterval> | undefined;

    const connect = () => {
      const token = tokenStore.getAccessToken();
      if (!token) return;

      const socket = new WebSocket(`${WS_URL}/ws/lists/${listId}?token=${encodeURIComponent(token)}`);
      socketRef.current = socket;

      socket.onopen = () => {
        reconnectAttempt.current = 0;
        heartbeat = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({ type: "PING" }));
        }, 25_000);
      };

      socket.onmessage = (event) => {
        const message: ListEvent = JSON.parse(event.data);
        const itemsKey = ["items", listId];

        switch (message.type) {
          case "ITEM_CREATED":
            queryClient.setQueryData<ShoppingItem[]>(itemsKey, (prev) =>
              prev?.some((i) => i.id === message.data.id) ? prev : [...(prev ?? []), message.data]
            );
            break;
          case "ITEM_UPDATED":
          case "ITEM_COMPLETED":
          case "ITEM_UNCOMPLETED":
            queryClient.setQueryData<ShoppingItem[]>(itemsKey, (prev) =>
              prev?.map((i) => (i.id === message.data.id ? message.data : i))
            );
            queryClient.invalidateQueries({ queryKey: ["lists", listId] });
            break;
          case "ITEM_DELETED":
            queryClient.setQueryData<ShoppingItem[]>(itemsKey, (prev) =>
              prev?.filter((i) => i.id !== message.data.id)
            );
            queryClient.invalidateQueries({ queryKey: ["lists", listId] });
            break;
          case "MEMBER_ADDED":
          case "MEMBER_REMOVED":
            queryClient.invalidateQueries({ queryKey: ["members", listId] });
            break;
        }
      };

      socket.onclose = () => {
        if (heartbeat) clearInterval(heartbeat);
        if (!shouldReconnect.current) return;
        const delay = Math.min(1000 * 2 ** reconnectAttempt.current, 15_000);
        reconnectAttempt.current += 1;
        setTimeout(connect, delay);
      };
    };

    connect();

    return () => {
      shouldReconnect.current = false;
      if (heartbeat) clearInterval(heartbeat);
      socketRef.current?.close();
    };
  }, [listId, queryClient]);
}
