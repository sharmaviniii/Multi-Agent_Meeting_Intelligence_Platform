import { Menu, Search, Sparkles, Upload, X } from "lucide-react";
import { useEffect, useId, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { MeetingWorkspace } from "@/features/meeting-workspace/meeting-workspace";
import { UploadDropzone } from "@/features/upload/upload-dropzone";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { cn } from "@/lib/utils";
import { toApiError, uploadMeeting } from "@/services/api";
import { type RecentMeeting, type UploadState } from "@/types/workspace";

const initialUploadState: UploadState = {
  fileName: "",
  progress: 0,
  status: "idle",
};

export function MeetingShell() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [recentMeetings, setRecentMeetings] = useState<RecentMeeting[]>([]);
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>(initialUploadState);
  const uploadAbortRef = useRef<AbortController | null>(null);
  const lastUploadRef = useRef<File | null>(null);
  const selectedMeeting = recentMeetings.find((meeting) => meeting.id === selectedMeetingId);

  useEffect(
    () => () => {
      uploadAbortRef.current?.abort();
    },
    [],
  );

  const handleFileAccepted = async (file: File) => {
    uploadAbortRef.current?.abort();
    const controller = new AbortController();
    uploadAbortRef.current = controller;
    lastUploadRef.current = file;
    setUploadState({ fileName: file.name, progress: 0, status: "uploading" });
    try {
      const meeting = await uploadMeeting(file, {
        onUploadProgress: (progress) =>
          setUploadState({ fileName: file.name, progress, status: "uploading" }),
        signal: controller.signal,
      });
      const recentMeeting: RecentMeeting = {
        filename: file.name,
        id: meeting.meeting_id,
        status: "uploaded",
        title: meeting.title,
        uploadedAt: new Date(meeting.date),
      };
      setRecentMeetings((currentMeetings) => [recentMeeting, ...currentMeetings]);
      setSelectedMeetingId(recentMeeting.id);
      setUploadState({ fileName: file.name, progress: 100, status: "complete" });
    } catch (error) {
      if (controller.signal.aborted) {
        return;
      }
      setUploadState({
        error: toApiError(error).message,
        fileName: file.name,
        progress: 0,
        status: "error",
      });
    }
  };

  return (
    <div className="min-h-dvh bg-background text-foreground">
      <div className="flex min-h-dvh">
        <MeetingSidebar
          className={cn(
            "fixed inset-y-0 left-0 z-40 hidden w-80 border-r border-border bg-background md:static md:flex",
            isSidebarOpen && "flex",
          )}
          meetings={recentMeetings}
          onClose={() => setIsSidebarOpen(false)}
          onSelectMeeting={setSelectedMeetingId}
          selectedMeetingId={selectedMeetingId}
        />
        {isSidebarOpen ? (
          <Button
            aria-label="Close sidebar"
            className="fixed inset-0 z-30 h-auto w-auto rounded-none bg-background/80 p-0 hover:bg-background/80 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
            type="button"
            variant="ghost"
          />
        ) : null}
        <div className="flex min-w-0 flex-1 flex-col">
          <AppHeader
            currentMeetingTitle={selectedMeeting?.title}
            onOpenSidebar={() => setIsSidebarOpen(true)}
          />
          <main aria-labelledby="workspace-title" className="flex min-h-0 flex-1 flex-col">
            <Breadcrumb selectedMeetingTitle={selectedMeeting?.title} />
            {selectedMeeting ? (
              <MeetingWorkspace meetingId={selectedMeeting.id} meetingTitle={selectedMeeting.title} />
            ) : (
              <UploadDropzone
                disabled={uploadState.status === "uploading"}
                onFileAccepted={handleFileAccepted}
                onRetry={() => {
                  if (lastUploadRef.current) {
                    void handleFileAccepted(lastUploadRef.current);
                  }
                }}
                uploadState={uploadState}
              />
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

type MeetingSidebarProps = {
  className?: string;
  meetings: RecentMeeting[];
  onClose: () => void;
  onSelectMeeting: (meetingId: string) => void;
  selectedMeetingId: string | null;
};

function MeetingSidebar({
  className,
  meetings,
  onClose,
  onSelectMeeting,
  selectedMeetingId,
}: MeetingSidebarProps) {
  const searchId = useId();
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 200);
  const visibleMeetings = useMemo(
    () =>
      meetings.filter((meeting) =>
        meeting.title.toLowerCase().includes(debouncedQuery.trim().toLowerCase()),
      ),
    [debouncedQuery, meetings],
  );

  return (
    <aside aria-label="Meetings" className={cn("flex h-dvh flex-col", className)}>
      <div className="flex h-16 items-center justify-between px-4">
        <a
          className="inline-flex items-center gap-3 rounded-md focus-visible:ring-2 focus-visible:ring-ring"
          href="/"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Sparkles aria-hidden="true" className="h-4 w-4" />
          </span>
          <span className="text-sm font-semibold">IntelMeet</span>
        </a>
        <Button
          aria-label="Close sidebar"
          className="md:hidden"
          onClick={onClose}
          size="icon"
          type="button"
          variant="ghost"
        >
          <X aria-hidden="true" className="h-4 w-4" />
        </Button>
      </div>
      <div className="px-4 pb-4">
        <Button className="w-full justify-start" type="button">
          <Upload aria-hidden="true" className="h-4 w-4" />
          Upload Meeting
        </Button>
      </div>
      <Separator />
      <nav aria-label="Meeting list" className="min-h-0 flex-1 overflow-y-auto p-3">
        <ul className="space-y-1">
          {visibleMeetings.map((meeting) => (
            <li key={meeting.id}>
              <button
                aria-current={meeting.id === selectedMeetingId ? "page" : undefined}
                className={cn(
                  "flex w-full flex-col items-start rounded-md px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:ring-2 focus-visible:ring-ring",
                  meeting.id === selectedMeetingId && "bg-accent text-accent-foreground",
                )}
                onClick={() => {
                  onSelectMeeting(meeting.id);
                  onClose();
                }}
                type="button"
              >
                <span className="w-full truncate font-medium">{meeting.title}</span>
                <time className="mt-1 text-xs text-muted-foreground">
                  {formatMeetingTime(meeting.uploadedAt)}
                </time>
              </button>
            </li>
          ))}
        </ul>
        {visibleMeetings.length === 0 && meetings.length === 0 ? (
          <p className="px-3 py-4 text-sm text-muted-foreground">No meetings yet.</p>
        ) : null}
        {visibleMeetings.length === 0 && meetings.length > 0 ? (
          <p className="px-3 py-4 text-sm text-muted-foreground">No matching meetings.</p>
        ) : null}
      </nav>
      <Separator />
      <form className="p-4" role="search">
        <label className="sr-only" htmlFor={searchId}>
          Search meetings
        </label>
        <div className="relative">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            id={searchId}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search meetings..."
            type="search"
            value={query}
            className="pl-9"
          />
        </div>
      </form>
    </aside>
  );
}

type AppHeaderProps = {
  currentMeetingTitle?: string;
  onOpenSidebar: () => void;
};

function AppHeader({ currentMeetingTitle, onOpenSidebar }: AppHeaderProps) {
  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-border px-4 md:px-6">
      <Button
        aria-label="Open sidebar"
        className="md:hidden"
        onClick={onOpenSidebar}
        size="icon"
        type="button"
        variant="ghost"
      >
        <Menu aria-hidden="true" className="h-4 w-4" />
      </Button>
      <div className="min-w-0">
        <p className="text-sm text-muted-foreground">IntelMeet</p>
        <h1 id="workspace-title" className="truncate text-base font-semibold">
          {currentMeetingTitle ?? "Upload Meeting"}
        </h1>
      </div>
    </header>
  );
}

function Breadcrumb({ selectedMeetingTitle }: { selectedMeetingTitle?: string }) {
  return (
    <nav aria-label="Breadcrumb" className="border-b border-border px-4 py-3 md:px-6">
      <ol className="flex items-center gap-2 text-sm text-muted-foreground">
        <li>
          <a
            className="rounded-md hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring"
            href="/"
          >
            Meetings
          </a>
        </li>
        <li aria-hidden="true">/</li>
        <li aria-current="page" className="text-foreground">
          {selectedMeetingTitle ?? "Upload"}
        </li>
      </ol>
    </nav>
  );
}

function formatMeetingTime(date: Date) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}
