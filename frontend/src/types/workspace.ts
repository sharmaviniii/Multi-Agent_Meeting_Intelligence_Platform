export type RecentMeeting = {
  id: string;
  filename: string;
  status: "uploaded";
  title: string;
  uploadedAt: Date;
};

export type UploadState = {
  error?: string;
  fileName: string;
  progress: number;
  status: "idle" | "uploading" | "complete" | "error";
};
