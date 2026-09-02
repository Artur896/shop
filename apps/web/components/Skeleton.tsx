import clsx from "clsx";

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-lg bg-neutral-200 dark:bg-neutral-800", className)} />;
}

export function ListCardSkeleton() {
  return (
    <div className="rounded-2xl border border-neutral-200 p-4 dark:border-neutral-800">
      <Skeleton className="mb-3 h-5 w-2/3" />
      <Skeleton className="mb-3 h-2 w-full" />
      <Skeleton className="h-4 w-1/3" />
    </div>
  );
}
