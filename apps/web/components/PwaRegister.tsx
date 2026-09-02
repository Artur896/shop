"use client";

import { useEffect } from "react";

export function PwaRegister() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        // Offline support degrades gracefully if registration fails (e.g. private browsing).
      });
    }
  }, []);
  return null;
}
