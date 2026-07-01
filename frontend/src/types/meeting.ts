export type MeetingId = string;

export type TranscriptTurn = {
  speaker: string;
  text: string;
  start_time?: string | null;
  end_time?: string | null;
};

export type Meeting = {
  meeting_id: MeetingId;
  title: string;
  date: string;
  participants: string[];
  transcript: TranscriptTurn[];
  summary: string;
};
