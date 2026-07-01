import { lazy, memo, Suspense, useCallback, useMemo, useState } from "react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WorkspaceTabSkeleton } from "@/features/meeting-workspace/workspace-tab-skeleton";
import { type WorkspaceTab, type WorkspaceTabId } from "@/features/meeting-workspace/types";

const TranscriptTab = lazy(() => import("@/features/meeting-workspace/tabs/transcript-tab"));
const SummaryTab = lazy(() => import("@/features/meeting-workspace/tabs/summary-tab"));
const ActionItemsTab = lazy(() => import("@/features/meeting-workspace/tabs/action-items-tab"));
const DecisionsTab = lazy(() => import("@/features/meeting-workspace/tabs/decisions-tab"));
const RisksTab = lazy(() => import("@/features/meeting-workspace/tabs/risks-tab"));
const EmailDraftTab = lazy(() => import("@/features/meeting-workspace/tabs/email-draft-tab"));

const tabs: WorkspaceTab[] = [
  { id: "transcript", label: "Transcript" },
  { id: "summary", label: "Summary" },
  { id: "action-items", label: "Action Items" },
  { id: "decisions", label: "Decisions" },
  { id: "risks", label: "Risks" },
  { id: "email-draft", label: "Email Draft" },
];
const tabIds = tabs.map((tab) => tab.id);

type MeetingWorkspaceProps = {
  meetingId: string;
  meetingTitle: string;
};

export const MeetingWorkspace = memo(function MeetingWorkspace({
  meetingId,
  meetingTitle,
}: MeetingWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<WorkspaceTabId>("transcript");
  const [visitedTabs, setVisitedTabs] = useState<Set<WorkspaceTabId>>(
    () => new Set(["transcript"]),
  );
  const mountedTabs = useMemo(() => tabs.filter((tab) => visitedTabs.has(tab.id)), [visitedTabs]);
  const handleTabChange = useCallback((nextTab: string) => {
    const tabId = nextTab as WorkspaceTabId;
    setActiveTab(tabId);
    setVisitedTabs((currentTabs) => {
      if (currentTabs.has(tabId)) {
        return currentTabs;
      }
      return new Set([...currentTabs, tabId]);
    });
  }, []);

  return (
    <Tabs
      aria-label="Meeting workspace"
      onValueChange={handleTabChange}
      value={activeTab}
      values={tabIds}
    >
      <TabsList>
        {tabs.map((tab) => (
          <TabsTrigger controls={`${tab.id}-panel`} key={tab.id} value={tab.id}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      <div className="min-h-0 flex-1">
        {mountedTabs.map((tab) => (
          <TabsContent key={tab.id} labelledBy={`${tab.id}-tab`} value={tab.id}>
            <Suspense fallback={<WorkspaceTabSkeleton />}>
              <TabContent meetingId={meetingId} meetingTitle={meetingTitle} tabId={tab.id} />
            </Suspense>
          </TabsContent>
        ))}
      </div>
    </Tabs>
  );
});

const TabContent = memo(function TabContent({
  meetingId,
  meetingTitle,
  tabId,
}: {
  meetingId: string;
  meetingTitle: string;
  tabId: WorkspaceTabId;
}) {
  if (tabId === "summary") {
    return <SummaryTab meetingId={meetingId} meetingTitle={meetingTitle} />;
  }
  if (tabId === "action-items") {
    return <ActionItemsTab meetingId={meetingId} meetingTitle={meetingTitle} />;
  }
  if (tabId === "decisions") {
    return <DecisionsTab meetingId={meetingId} />;
  }
  if (tabId === "risks") {
    return <RisksTab meetingId={meetingId} />;
  }
  if (tabId === "email-draft") {
    return <EmailDraftTab meetingId={meetingId} />;
  }
  return <TranscriptTab meetingId={meetingId} />;
});
