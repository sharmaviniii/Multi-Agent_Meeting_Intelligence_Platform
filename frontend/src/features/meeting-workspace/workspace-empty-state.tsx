import { type ReactNode } from "react";

type WorkspaceEmptyStateProps = {
  description: string;
  icon: ReactNode;
  title: string;
};

export function WorkspaceEmptyState({ description, icon, title }: WorkspaceEmptyStateProps) {
  return (
    <div className="flex min-h-80 items-center justify-center px-4 py-10 md:px-6">
      <div className="max-w-md text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg border border-border bg-muted text-muted-foreground">
          {icon}
        </div>
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
