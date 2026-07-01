import { Clock, MessageSquareText, Smile, Sparkles, Users } from "lucide-react";
import { type ReactNode, useCallback } from "react";

import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { getSummary, type Meeting } from "@/services/api";

type SummaryTabProps = {
  meetingId: string;
  meetingTitle: string;
};

export default function SummaryTab({ meetingId, meetingTitle }: SummaryTabProps) {
  const loadSummary = useCallback(
    (signal: AbortSignal) => getSummary(meetingId, { signal }),
    [meetingId],
  );
  const summaryState = useRequestState(
    loadSummary,
    (meeting) => !meeting.summary && meeting.participants.length === 0,
    [loadSummary],
  );

  return (
    <div className="h-full overflow-y-auto">
      <article className="mx-auto w-full max-w-6xl px-4 py-6 md:px-6">
        <header className="mb-4">
          <p className="text-sm text-muted-foreground">{meetingTitle}</p>
          <h2 className="mt-1 text-lg font-semibold">Summary</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            A calm meeting brief will appear here when analysis is available.
          </p>
        </header>
        <TabStatus empty={<EmptySummary />} state={summaryState}>
          {(meeting) => <SummaryContent meeting={meeting} />}
        </TabStatus>
      </article>
    </div>
  );
}

function SummaryContent({ meeting }: { meeting: Meeting }) {
  return (
    <>
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.5fr)_minmax(20rem,1fr)]">
        <SummaryCard
          className="lg:row-span-2"
          description={meeting.summary || "No executive summary was returned."}
          icon={<Sparkles aria-hidden="true" className="h-5 w-5" />}
          title="Executive Summary"
        />
        <SummaryCard
          description="Topics will appear once analysis completes."
          icon={<MessageSquareText aria-hidden="true" className="h-5 w-5" />}
          title="Key Topics"
        />
        <SummaryCard
          description="Sentiment analysis is not available for this meeting yet."
          icon={<Smile aria-hidden="true" className="h-5 w-5" />}
          title="Sentiment"
        />
        <SummaryCard
          description="Meeting duration will appear after timestamp analysis completes."
          icon={<Clock aria-hidden="true" className="h-5 w-5" />}
          title="Duration"
        />
        <SummaryCard
          description={meeting.participants.join(", ") || "No participants were identified."}
          icon={<Users aria-hidden="true" className="h-5 w-5" />}
          title="Participants"
        />
      </div>
      <section className="mt-4 rounded-lg border border-border bg-card p-4">
        <h3 className="text-sm font-semibold">Important Decisions</h3>
        <WorkspaceEmptyState
          description="Highlighted decisions will appear after decision extraction completes."
          icon={<Sparkles aria-hidden="true" className="h-5 w-5" />}
          title="No highlighted decisions"
        />
      </section>
    </>
  );
}

function EmptySummary() {
  return (
    <WorkspaceEmptyState
      description="A summary will appear once this meeting has enough analysis to show."
      icon={<Sparkles aria-hidden="true" className="h-5 w-5" />}
      title="No summary yet"
    />
  );
}

type SummaryCardProps = {
  className?: string;
  description: string;
  icon: ReactNode;
  title: string;
};

function SummaryCard({ className, description, icon, title }: SummaryCardProps) {
  return (
    <section className={className}>
      <div className="h-full rounded-lg border border-border bg-card p-4">
        <div className="mb-4 flex h-9 w-9 items-center justify-center rounded-md bg-muted text-muted-foreground">
          {icon}
        </div>
        <h3 className="text-sm font-semibold">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
    </section>
  );
}
