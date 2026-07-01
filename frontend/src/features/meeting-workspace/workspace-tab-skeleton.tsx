import { Skeleton } from "@/components/ui/skeleton";

export function WorkspaceTabSkeleton() {
  return (
    <div aria-label="Loading workspace tab" className="space-y-4 px-4 py-6 md:px-6" role="status">
      <Skeleton className="h-5 w-40" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-24 w-full" />
      <span className="sr-only">Loading</span>
    </div>
  );
}
