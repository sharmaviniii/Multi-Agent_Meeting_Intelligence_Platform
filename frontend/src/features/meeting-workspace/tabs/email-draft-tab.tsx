import { ClipboardCopy, Download, Mail, Send } from "lucide-react";
import { useCallback, useMemo } from "react";

import { Button } from "@/components/ui/button";
import { TabStatus, useRequestState } from "@/features/meeting-workspace/request-state";
import { WorkspaceEmptyState } from "@/features/meeting-workspace/workspace-empty-state";
import { getEmailDraft, type EmailDraft } from "@/services/api";

export default function EmailDraftTab({ meetingId }: { meetingId: string }) {
  const loadEmailDraft = useCallback(
    (signal: AbortSignal) => getEmailDraft(meetingId, { signal }),
    [meetingId],
  );
  const draftState = useRequestState(loadEmailDraft, (draft) => !draft.body, [loadEmailDraft]);
  const emailDraft = draftState.status === "success" ? draftState.data : null;
  const draftText = useMemo(() => {
    if (!emailDraft) {
      return "";
    }
    return `To: ${emailDraft.recipient ?? ""}\nSubject: ${emailDraft.subject}\n\n${
      emailDraft.body
    }`;
  }, [emailDraft]);
  const hasDraft = emailDraft !== null;
  const copyDraft = useCallback(() => {
    if (draftText && navigator.clipboard) {
      void navigator.clipboard.writeText(draftText);
    }
  }, [draftText]);
  const exportDraft = useCallback(() => {
    if (!draftText) {
      return;
    }
    const url = URL.createObjectURL(new Blob([draftText], { type: "text/plain" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "email-draft.txt";
    link.click();
    URL.revokeObjectURL(url);
  }, [draftText]);

  return (
    <div className="h-full overflow-y-auto px-4 py-6 md:px-6">
      <article className="mx-auto w-full max-w-3xl">
        <header className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Email Draft</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Drafts stay readable, editable-ready, and close to the meeting context.
            </p>
          </div>
          <div aria-label="Email draft exports" className="flex gap-2">
            <Button disabled={!hasDraft} onClick={copyDraft} type="button" variant="outline">
              <ClipboardCopy aria-hidden="true" className="h-4 w-4" />
              Copy
            </Button>
            <Button disabled={!hasDraft} onClick={exportDraft} type="button" variant="outline">
              <Download aria-hidden="true" className="h-4 w-4" />
              Export
            </Button>
          </div>
        </header>
        <TabStatus empty={<EmptyEmailDraft />} state={draftState}>
          {(draft) => <EmailDraftContent draft={draft} />}
        </TabStatus>
      </article>
    </div>
  );
}

function EmailDraftContent({ draft }: { draft: EmailDraft }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4">
      <header className="mb-4 flex items-start gap-3">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
          <Send aria-hidden="true" className="h-4 w-4" />
        </span>
        <div>
          <p className="text-sm font-semibold">{draft.subject}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {draft.recipient ?? "No recipient"} - {draft.tone ?? "professional"}
          </p>
        </div>
      </header>
      <pre className="whitespace-pre-wrap font-sans text-sm leading-6">{draft.body}</pre>
    </section>
  );
}

function EmptyEmailDraft() {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <WorkspaceEmptyState
        description="A follow-up email will appear after backend generation returns recipient, subject, body, and tone."
        icon={<Mail aria-hidden="true" className="h-5 w-5" />}
        title="No email draft"
      />
    </div>
  );
}
