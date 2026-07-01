import { BadgeCheck, Quote } from "lucide-react";
import { memo, useCallback } from "react";

import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { getDecisions, type Decision } from "@/services/api";

type DecisionCard = {
  id: string;
  description: string;
  owner?: string;
  rationale?: string;
  sourceQuote?: string;
};

export default function DecisionsTab({ meetingId }: { meetingId: string }) {
  const loadDecisions = useCallback(
    (signal: AbortSignal) => getDecisions(meetingId, { signal }),
    [meetingId],
  );
  const decisionsState = useRequestState(
    loadDecisions,
    (items) => items.length === 0,
    [loadDecisions],
  );

  return (
    <div className="h-full overflow-y-auto px-4 py-6 md:px-6">
      <section className="mx-auto w-full max-w-4xl" aria-labelledby="decisions-title">
        <header className="mb-4">
          <h2 id="decisions-title" className="text-lg font-semibold">
            Decisions
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Confirmed outcomes are separated from discussion so they are easy to scan.
          </p>
        </header>
        <TabStatus empty={<EmptyDecisions />} state={decisionsState}>
          {(items) => <DecisionList items={toDecisionCards(items)} />}
        </TabStatus>
      </section>
    </div>
  );
}

const DecisionList = memo(function DecisionList({ items }: { items: DecisionCard[] }) {
  return (
    <ol className="space-y-3" role="list">
      {items.map((item) => (
        <li key={item.id}>
          <article className="rounded-lg border border-border bg-card p-4">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
                <BadgeCheck aria-hidden="true" className="h-4 w-4" />
              </span>
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold">{item.description}</h3>
                <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                  <DecisionMeta label="Owner" value={item.owner ?? "Unassigned"} />
                  <DecisionMeta label="Rationale" value={item.rationale ?? "No rationale"} />
                </dl>
                {item.sourceQuote ? (
                  <blockquote className="mt-4 border-l border-border pl-3 text-sm text-muted-foreground">
                    <Quote aria-hidden="true" className="mb-2 h-4 w-4" />
                    {item.sourceQuote}
                  </blockquote>
                ) : null}
              </div>
            </div>
          </article>
        </li>
      ))}
    </ol>
  );
});

function DecisionMeta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}

function EmptyDecisions() {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <WorkspaceEmptyState
        description="Decision cards will appear after backend extraction returns outcomes, owners, rationale, and source quotes."
        icon={<BadgeCheck aria-hidden="true" className="h-5 w-5" />}
        title="No decisions"
      />
    </div>
  );
}

function toDecisionCards(items: Decision[]): DecisionCard[] {
  return items.map((item) => ({
    description: item.description,
    id: item.id,
    owner: item.owner ?? undefined,
    rationale: item.rationale ?? undefined,
    sourceQuote: item.source_quote ?? undefined,
  }));
}
