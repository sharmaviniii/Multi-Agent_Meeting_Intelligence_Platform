import { ClipboardCopy, Download, ListChecks } from "lucide-react";
import { memo, useCallback, useMemo } from "react";

import { Button } from "@/components/ui/button";
import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { getActionItems, type ActionItem } from "@/services/api";

type TaskCard = {
  id: string;
  title: string;
  owner?: string;
  dueDate?: string;
  priority?: string;
  status?: string;
};

type ActionItemsTabProps = {
  meetingId: string;
  meetingTitle: string;
};

export default function ActionItemsTab({ meetingId, meetingTitle }: ActionItemsTabProps) {
  const loadActionItems = useCallback(
    (signal: AbortSignal) => getActionItems(meetingId, { signal }),
    [meetingId],
  );
  const actionState = useRequestState(
    loadActionItems,
    (items) => items.length === 0,
    [loadActionItems],
  );
  const loadedItems = actionState.status === "success" ? toTaskCards(actionState.data) : [];
  const exportText = useMemo(
    () =>
      loadedItems
        .map(
          (item) =>
            `${item.title}\nOwner: ${item.owner ?? "Unassigned"}\nDue: ${
              item.dueDate ?? "No due date"
            }\nPriority: ${item.priority ?? "medium"}\nStatus: ${item.status ?? "open"}`,
        )
        .join("\n\n"),
    [loadedItems],
  );
  const hasActions = loadedItems.length > 0;
  const copyActions = useCallback(() => {
    if (exportText && navigator.clipboard) {
      void navigator.clipboard.writeText(exportText);
    }
  }, [exportText]);
  const exportActions = useCallback(() => {
    if (!exportText) {
      return;
    }
    const url = URL.createObjectURL(new Blob([exportText], { type: "text/plain" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${meetingTitle}-action-items.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }, [exportText, meetingTitle]);

  return (
    <div className="h-full overflow-y-auto px-4 py-6 md:px-6">
      <section className="mx-auto w-full max-w-4xl" aria-labelledby="action-items-title">
        <header className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{meetingTitle}</p>
            <h2 id="action-items-title" className="mt-1 text-lg font-semibold">
              Action Items
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Tasks are organized by owner, due date, priority, and status.
            </p>
          </div>
          <div className="flex gap-2">
            <Button disabled={!hasActions} onClick={copyActions} type="button" variant="outline">
              <ClipboardCopy aria-hidden="true" className="h-4 w-4" />
              Copy
            </Button>
            <Button disabled={!hasActions} onClick={exportActions} type="button" variant="outline">
              <Download aria-hidden="true" className="h-4 w-4" />
              Export
            </Button>
          </div>
        </header>
        <TabStatus empty={<EmptyActionItems />} state={actionState}>
          {(items) => <TaskCardList items={toTaskCards(items)} />}
        </TabStatus>
      </section>
    </div>
  );
}

const TaskCardList = memo(function TaskCardList({ items }: { items: TaskCard[] }) {
  return (
    <ul className="grid gap-3" role="list">
      {items.map((item) => (
        <li key={item.id}>
          <article className="rounded-lg border border-border bg-card p-4">
            <h3 className="text-sm font-semibold">{item.title}</h3>
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
              <TaskMeta label="Owner" value={item.owner ?? "Unassigned"} />
              <TaskMeta label="Due date" value={item.dueDate ?? "No due date"} />
              <TaskMeta label="Priority" value={item.priority ?? "medium"} />
              <TaskMeta label="Status" value={item.status ?? "open"} />
            </dl>
          </article>
        </li>
      ))}
    </ul>
  );
});

function TaskMeta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 rounded-md bg-muted px-2 py-1 text-xs font-medium">{value}</dd>
    </div>
  );
}

function EmptyActionItems() {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="mb-4 grid gap-3 sm:grid-cols-4">
        <TaskFieldPlaceholder label="Owner" />
        <TaskFieldPlaceholder label="Due date" />
        <TaskFieldPlaceholder label="Priority" />
        <TaskFieldPlaceholder label="Status" />
      </div>
      <WorkspaceEmptyState
        description="Task cards will appear after backend extraction returns owner, due date, priority, and status."
        icon={<ListChecks aria-hidden="true" className="h-5 w-5" />}
        title="No action items"
      />
    </div>
  );
}

function TaskFieldPlaceholder({ label }: { label: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 h-2 w-16 rounded-full bg-muted" />
    </div>
  );
}

function toTaskCards(items: ActionItem[]): TaskCard[] {
  return items.map((item) => ({
    dueDate: item.due_date ?? undefined,
    id: item.id,
    owner: item.owner ?? undefined,
    priority: item.priority,
    status: item.status,
    title: item.description,
  }));
}
