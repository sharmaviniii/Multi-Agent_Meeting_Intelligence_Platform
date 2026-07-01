import { FileText } from "lucide-react";
import { memo, useCallback, useMemo } from "react";

import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { cn } from "@/lib/utils";
import { getTranscript, type TranscriptTurn as ApiTranscriptTurn } from "@/services/api";

type TranscriptTurn = {
  id: string;
  speaker: string;
  text: string;
  timestamp?: string;
};

type TranscriptTabProps = {
  meetingId: string;
};

export default function TranscriptTab({ meetingId }: TranscriptTabProps) {
  const loadTranscript = useCallback(
    (signal: AbortSignal) => getTranscript(meetingId, { signal }),
    [meetingId],
  );
  const transcriptState = useRequestState(
    loadTranscript,
    (turns) => turns.length === 0,
    [loadTranscript],
  );

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto w-full max-w-5xl px-4 py-6 md:px-6">
        <header className="mb-4">
          <h2 className="text-lg font-semibold">Transcript</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Conversation turns are grouped by speaker for fast review.
          </p>
        </header>
        <TabStatus
          empty={
            <TranscriptEmpty description="No transcript content was returned for this meeting." />
          }
          state={transcriptState}
        >
          {(turns) => <TranscriptList turns={toTranscriptTurns(turns)} />}
        </TabStatus>
      </div>
    </div>
  );
}

const TranscriptList = memo(function TranscriptList({ turns }: { turns: TranscriptTurn[] }) {
  const speakerIndexes = useMemo(() => {
    const indexes = new Map<string, number>();
    turns.forEach((turn) => {
      if (!indexes.has(turn.speaker)) {
        indexes.set(turn.speaker, indexes.size);
      }
    });
    return indexes;
  }, [turns]);

  if (turns.length === 0) {
    return (
      <div className="min-h-96 rounded-lg border border-border">
        <TranscriptEmpty description="No transcript content is available yet. Chat bubbles will render in this virtualized-ready list." />
      </div>
    );
  }

  return (
    <ol
      aria-label="Transcript conversation"
      className="space-y-4"
      data-virtualized-ready="true"
      role="list"
    >
      {turns.map((turn) => (
        <TranscriptBubble
          key={turn.id}
          speakerIndex={speakerIndexes.get(turn.speaker) ?? 0}
          turn={turn}
        />
      ))}
    </ol>
  );
});

const TranscriptBubble = memo(function TranscriptBubble({
  speakerIndex,
  turn,
}: {
  speakerIndex: number;
  turn: TranscriptTurn;
}) {
  const isAlternate = speakerIndex % 2 === 1;

  return (
    <li
      className={cn(
        "flex gap-3 rounded-lg border border-border p-3",
        isAlternate ? "bg-secondary" : "bg-card",
      )}
    >
      <span className="sticky top-3 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
        {speakerInitials(turn.speaker)}
      </span>
      <article className="min-w-0 flex-1">
        <header className="sticky top-0 z-10 mb-2 flex flex-wrap items-center gap-2 bg-inherit py-1">
          <h3 className="text-sm font-semibold">{turn.speaker}</h3>
          {turn.timestamp ? (
            <time className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
              {turn.timestamp}
            </time>
          ) : null}
        </header>
        <p className="text-sm leading-6 text-foreground">{turn.text}</p>
      </article>
    </li>
  );
});

function speakerInitials(speaker: string) {
  return speaker
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

function TranscriptEmpty({ description }: { description: string }) {
  return (
    <WorkspaceEmptyState
      description={description}
      icon={<FileText aria-hidden="true" className="h-5 w-5" />}
      title="No transcript available"
    />
  );
}

function toTranscriptTurns(turns: ApiTranscriptTurn[]): TranscriptTurn[] {
  return turns.slice(0, 100).map((turn, index) => ({
    id: `${turn.speaker}-${index}`,
    speaker: turn.speaker,
    text: turn.text,
    timestamp: turn.start_time ?? undefined,
  }));
}
