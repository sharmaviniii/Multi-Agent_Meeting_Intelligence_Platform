export type WorkspaceTabId =
  | "transcript"
  | "summary"
  | "action-items"
  | "decisions"
  | "risks"
  | "email-draft";

export type WorkspaceTab = {
  id: WorkspaceTabId;
  label: string;
};
