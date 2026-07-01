export const queryKeys = {
  meetings: {
    all: ["meetings"] as const,
    lists: () => [...queryKeys.meetings.all, "list"] as const,
    detail: (meetingId: string) => [...queryKeys.meetings.all, "detail", meetingId] as const,
  },
};
