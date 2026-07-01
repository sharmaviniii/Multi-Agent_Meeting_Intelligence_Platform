import { type ReactNode, useEffect, useState } from "react";

import { WorkspaceTabSkeleton } from "@/features/meeting-workspace/workspace-tab-skeleton";
import { type ApiError, type RequestState, toApiError } from "@/services/api";

export function useRequestState<TData>(
  load: (signal: AbortSignal) => Promise<TData>,
  isEmpty: (data: TData) => boolean,
  deps: readonly unknown[],
) {
  const [state, setState] = useState<RequestState<TData>>({ status: "idle" });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading" });
    load(controller.signal)
      .then((data) => {
        setState(isEmpty(data) ? { status: "empty" } : { data, status: "success" });
      })
      .catch((error) => {
        if (!controller.signal.aborted) {
          setState({ error: toApiError(error), status: "error" });
        }
      });

    return () => controller.abort();
  }, deps);

  return state;
}

export function TabStatus<TData>({
  children,
  empty,
  state,
}: {
  children: (data: TData) => ReactNode;
  empty: ReactNode;
  state: RequestState<TData>;
}) {
  if (state.status === "idle" || state.status === "loading") {
    return <WorkspaceTabSkeleton />;
  }
  if (state.status === "error") {
    return <TabError error={state.error} />;
  }
  if (state.status === "empty") {
    return empty;
  }
  return children(state.data);
}

function TabError({ error }: { error: ApiError }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <h3 className="text-sm font-semibold">Request failed</h3>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{error.message}</p>
      {error.requestId ? (
        <p className="mt-3 text-xs text-muted-foreground">Request ID: {error.requestId}</p>
      ) : null}
    </section>
  );
}
