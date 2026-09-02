"use client";

import { useState } from "react";
import { useAuth } from "@/features/auth/AuthContext";
import { useLists } from "@/features/lists/hooks";
import { ListCard } from "@/features/lists/ListCard";
import { CreateListModal } from "@/features/lists/CreateListModal";
import { EmptyState } from "@/components/EmptyState";
import { ListCardSkeleton } from "@/components/Skeleton";
import { InstallBanner } from "@/components/InstallBanner";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useLists();
  const [createOpen, setCreateOpen] = useState(false);

  const firstName = user?.name.split(" ")[0];

  return (
    <div className="mx-auto max-w-2xl px-4 pt-6">
      <h1 className="text-2xl font-semibold">Hola, {firstName} 👋</h1>
      <InstallBanner />

      <section className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="font-medium text-neutral-700 dark:text-neutral-300">Mis listas</h2>
          <button
            onClick={() => setCreateOpen(true)}
            className="tap-target rounded-full bg-brand-600 px-4 text-sm font-medium text-white active:scale-95"
          >
            + Nueva lista
          </button>
        </div>

        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {[1, 2].map((i) => (
              <ListCardSkeleton key={i} />
            ))}
          </div>
        ) : data && data.mine.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {data.mine.map((list) => (
              <ListCard key={list.id} list={list} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon="🛒"
            title="Aún no tienes listas"
            description="Crea tu primera lista de compras para empezar"
            action={
              <button
                onClick={() => setCreateOpen(true)}
                className="tap-target rounded-full bg-brand-600 px-5 text-sm font-medium text-white"
              >
                Crear lista
              </button>
            }
          />
        )}
      </section>

      {data && data.shared.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-3 font-medium text-neutral-700 dark:text-neutral-300">Compartidas conmigo</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {data.shared.map((list) => (
              <ListCard key={list.id} list={list} />
            ))}
          </div>
        </section>
      )}

      <CreateListModal open={createOpen} onClose={() => setCreateOpen(false)} />
    </div>
  );
}
