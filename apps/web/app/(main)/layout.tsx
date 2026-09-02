"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/features/auth/AuthContext";
import { BottomNav, Sidebar } from "@/components/NavShell";
import { OfflineBanner } from "@/components/OfflineBanner";
import { useOfflineSync } from "@/hooks/useOfflineSync";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  useOfflineSync();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return <div className="flex min-h-screen items-center justify-center text-neutral-400">Cargando…</div>;
  }

  return (
    <div className="min-h-screen sm:pl-60">
      <Sidebar />
      <OfflineBanner />
      <main className="pb-20 sm:pb-6">{children}</main>
      <BottomNav />
    </div>
  );
}
