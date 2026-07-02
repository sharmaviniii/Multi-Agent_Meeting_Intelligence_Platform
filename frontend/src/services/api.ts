import axios, { AxiosError, type AxiosProgressEvent } from "axios";
import { z } from "zod";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000",
  timeout: 60_000,
});

api.interceptors.request.use((config) => {
  config.headers.set("X-Request-ID", crypto.randomUUID());
  return config;
});

const transcriptTurnSchema = z.object({
  speaker: z.string(),
  text: z.string(),
  start_time: z.string().nullable(),
  end_time: z.string().nullable(),
});

const actionItemSchema = z.object({
  id: z.string(),
  description: z.string(),
  owner: z.string().nullable(),
  due_date: z.string().nullable(),
  priority: z.string(),
  status: z.string(),
  source_quote: z.string().nullable(),
});

const decisionSchema = z.object({
  id: z.string(),
  description: z.string(),
  owner: z.string().nullable(),
  rationale: z.string().nullable(),
  source_quote: z.string().nullable(),
});

const riskSchema = z.object({
  id: z.string(),
  description: z.string(),
  severity: z.string(),
  probability: z.string(),
  mitigation: z.string().nullable(),
  owner: z.string().nullable(),
  status: z.string(),
});

const emailDraftSchema = z.object({
  id: z.string(),
  recipient: z.string().nullable(),
  subject: z.string(),
  body: z.string(),
  tone: z.string(),
});

const meetingSchema = z.object({
  meeting_id: z.string(),
  title: z.string(),
  date: z.string(),
  participants: z.array(z.string()),
  transcript: z.array(transcriptTurnSchema),
  summary: z.string(),
  action_items: z.array(actionItemSchema),
  decisions: z.array(decisionSchema),
  risks: z.array(riskSchema),
  follow_ups: z.array(emailDraftSchema),
  embeddings_metadata: z
    .object({
      analysis_mode: z.enum(["llm", "heuristic"]).optional(),
    })
    .catchall(z.unknown())
    .default({}),
});

const meetingResponseSchema = z.object({ meeting: meetingSchema });
const actionItemsResponseSchema = z.object({
  meeting_id: z.string(),
  action_items: z.array(actionItemSchema),
});
const decisionsResponseSchema = z.object({
  meeting_id: z.string(),
  decisions: z.array(decisionSchema),
});
const risksResponseSchema = z.object({
  meeting_id: z.string(),
  risks: z.array(riskSchema),
});
const emailDraftResponseSchema = z.object({
  meeting_id: z.string(),
  email: emailDraftSchema,
});

export type Meeting = z.infer<typeof meetingSchema>;
export type TranscriptTurn = z.infer<typeof transcriptTurnSchema>;
export type ActionItem = z.infer<typeof actionItemSchema>;
export type Decision = z.infer<typeof decisionSchema>;
export type Risk = z.infer<typeof riskSchema>;
export type EmailDraft = z.infer<typeof emailDraftSchema>;

export type RequestState<TData> =
  | { status: "idle"; data?: undefined; error?: undefined }
  | { status: "loading"; data?: undefined; error?: undefined }
  | { status: "success"; data: TData; error?: undefined }
  | { status: "empty"; data?: undefined; error?: undefined }
  | { status: "error"; data?: undefined; error: ApiError };

export type ApiError = {
  message: string;
  requestId?: string;
  status?: number;
  type: "network" | "not_found" | "client" | "server" | "malformed";
};

type RequestOptions = {
  signal?: AbortSignal;
};

export async function uploadMeeting(
  file: File,
  options: RequestOptions & { onUploadProgress?: (progress: number) => void } = {},
) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event: AxiosProgressEvent) => {
      if (!event.total) {
        return;
      }
      options.onUploadProgress?.(Math.round((event.loaded / event.total) * 100));
    },
    signal: options.signal,
  });
  return parseResponse(meetingResponseSchema, response.data).meeting;
}

export async function getTranscript(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/transcript/${meetingId}`, { signal: options.signal });
  return parseResponse(meetingResponseSchema, response.data).meeting.transcript;
}

export async function getSummary(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/summary/${meetingId}`, { signal: options.signal });
  return parseResponse(meetingResponseSchema, response.data).meeting;
}

export async function getActionItems(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/action-items/${meetingId}`, { signal: options.signal });
  return parseResponse(actionItemsResponseSchema, response.data).action_items;
}

export async function getDecisions(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/decisions/${meetingId}`, { signal: options.signal });
  return parseResponse(decisionsResponseSchema, response.data).decisions;
}

export async function getRisks(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/risks/${meetingId}`, { signal: options.signal });
  return parseResponse(risksResponseSchema, response.data).risks;
}

export async function getEmailDraft(meetingId: string, options: RequestOptions = {}) {
  const response = await api.get(`/email-draft/${meetingId}`, { signal: options.signal });
  return parseResponse(emailDraftResponseSchema, response.data).email;
}

export function toApiError(error: unknown): ApiError {
  if (error instanceof z.ZodError) {
    return {
      message: "The backend returned a response shape the frontend does not understand.",
      type: "malformed",
    };
  }
  if (axios.isCancel(error)) {
    return { message: "The request was cancelled.", type: "network" };
  }
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const requestId = error.response?.headers["x-request-id"];
    const detail = extractErrorDetail(error.response?.data);
    if (!status) {
      return {
        message: "Could not reach the backend. Confirm FastAPI is running on VITE_API_URL.",
        requestId,
        type: "network",
      };
    }
    if (status === 404) {
      return {
        message: detail ?? "This meeting artifact is not available yet.",
        requestId,
        status,
        type: "not_found",
      };
    }
    if (status >= 500) {
      return {
        message:
          detail ??
          "The backend failed while processing this meeting. Try again after checking logs.",
        requestId,
        status,
        type: "server",
      };
    }
    return {
      message: detail ?? `The backend rejected this request with HTTP ${status}.`,
      requestId,
      status,
      type: "client",
    };
  }
  return {
    message: "An unexpected frontend error interrupted the request.",
    type: "malformed",
  };
}

function parseResponse<TSchema extends z.ZodTypeAny>(schema: TSchema, data: unknown) {
  return schema.parse(data) as z.infer<TSchema>;
}

function extractErrorDetail(data: unknown) {
  const result = z.object({ detail: z.string() }).safeParse(data);
  return result.success ? result.data.detail : undefined;
}
