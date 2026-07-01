import { ShieldAlert } from "lucide-react";
import { memo, useCallback } from "react";

import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { getRisks, type Risk } from "@/services/api";

type RiskCard = {
  id: string;
  description: string;
  mitigation?: string;
  owner?: string;
  probability?: string;
  severity?: string;
  status?: string;
};

export default function RisksTab({ meetingId }: { meetingId: string }) {
  const loadRisks = useCallback(
    (signal: AbortSignal) => getRisks(meetingId, { signal }),
    [meetingId],
  );
  const risksState = useRequestState(loadRisks, (items) => items.length === 0, [loadRisks]);

  return (
    <div className="h-full overflow-y-auto px-4 py-6 md:px-6">
      <section className="mx-auto w-full max-w-4xl" aria-labelledby="risks-title">
        <header className="mb-4">
          <h2 id="risks-title" className="text-lg font-semibold">
            Risks
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Risks are framed as operational follow-through, not alarm bells.
          </p>
        </header>
        <TabStatus empty={<EmptyRisks />} state={risksState}>
          {(items) => <RiskList items={toRiskCards(items)} />}
        </TabStatus>
      </section>
    </div>
  );
}

const RiskList = memo(function RiskList({ items }: { items: RiskCard[] }) {
  return (
    <ul className="grid gap-3" role="list">
      {items.map((item) => (
        <li key={item.id}>
          <article className="rounded-lg border border-border bg-card p-4">
            <header className="flex items-start gap-3">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
                <ShieldAlert aria-hidden="true" className="h-4 w-4" />
              </span>
              <div>
                <h3 className="text-sm font-semibold">{item.description}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.mitigation ?? "No mitigation captured yet."}
                </p>
              </div>
            </header>
            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
              <RiskMeta label="Severity" value={item.severity ?? "medium"} />
              <RiskMeta label="Probability" value={item.probability ?? "medium"} />
              <RiskMeta label="Owner" value={item.owner ?? "Unassigned"} />
              <RiskMeta label="Status" value={item.status ?? "open"} />
            </dl>
          </article>
        </li>
      ))}
    </ul>
  );
});

function RiskMeta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 rounded-md bg-muted px-2 py-1 text-xs font-medium">{value}</dd>
    </div>
  );
}

function EmptyRisks() {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <WorkspaceEmptyState
        description="Risk cards will appear after backend extraction returns severity, probability, mitigation, and owner."
        icon={<ShieldAlert aria-hidden="true" className="h-5 w-5" />}
        title="No risks"
      />
    </div>
  );
}

function toRiskCards(items: Risk[]): RiskCard[] {
  return items.map((item) => ({
    description: item.description,
    id: item.id,
    mitigation: item.mitigation ?? undefined,
    owner: item.owner ?? undefined,
    probability: item.probability,
    severity: item.severity,
    status: item.status,
  }));
}
