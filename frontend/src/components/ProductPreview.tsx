import { useState } from "react";
import { FileText, Sparkles, ListChecks, GitCommitHorizontal, ShieldAlert, Mail, Upload } from "lucide-react";
import { Container, SectionHeading } from "./shared";

const TABS = [
  { id: "transcript", label: "Transcript", icon: FileText },
  { id: "summary", label: "Summary", icon: Sparkles },
  { id: "actions", label: "Action Items", icon: ListChecks },
  { id: "decisions", label: "Decisions", icon: GitCommitHorizontal },
  { id: "risks", label: "Risks", icon: ShieldAlert },
  { id: "email", label: "Email", icon: Mail },
] as const;

type TabId = (typeof TABS)[number]["id"];

const MEETINGS = ["Product Sync — Jul 12", "Vendor Review — Jul 10", "Sprint Planning — Jul 8"];

function TabContent({ tab }: { tab: TabId }) {
  switch (tab) {
    case "transcript":
      return (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 font-mono text-xs leading-relaxed text-slate-200">
          <p><span className="text-blue-400">Asha:</span> We need the demo ready by Friday.</p>
          <p><span className="text-blue-400">Rahul:</span> I&apos;ll finish the API by Thursday.</p>
          <p><span className="text-blue-400">Priya:</span> I&apos;ll confirm the vendor SLA this week.</p>
        </div>
      );
    case "summary":
      return (
        <div className="space-y-3">
          <div className="h-2.5 w-full rounded-full bg-slate-100" />
          <div className="h-2.5 w-11/12 rounded-full bg-slate-100" />
          <div className="h-2.5 w-4/5 rounded-full bg-slate-100" />
          <p className="pt-2 text-sm leading-relaxed text-slate-600">
            Team aligned on the Q3 launch date. Two blockers were flagged and assigned owners before the meeting closed.
          </p>
        </div>
      );
    case "actions":
      return (
        <ul className="space-y-2">
          {[
            ["Rahul", "Finish the API", "Thu"],
            ["Priya", "Confirm vendor SLA", "Fri"],
            ["Asha", "Prep demo script", "Fri"],
          ].map(([owner, task, due]) => (
            <li
              key={task}
              className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
            >
              <span className="text-slate-700">{task}</span>
              <span className="flex items-center gap-2 text-xs text-slate-400">
                <span className="rounded-full bg-white px-2 py-0.5 border border-slate-200">{owner}</span>
                {due}
              </span>
            </li>
          ))}
        </ul>
      );
    case "decisions":
      return (
        <ul className="space-y-2">
          {["Ship v1 without SSO", "Use ChromaDB for retrieval", "Delay pricing page to Phase 2"].map((d) => (
            <li key={d} className="flex items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-700">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-600" /> {d}
            </li>
          ))}
        </ul>
      );
    case "risks":
      return (
        <ul className="space-y-2">
          {["Vendor SLA unconfirmed", "No fallback for embedding provider outage"].map((r) => (
            <li key={r} className="flex items-center gap-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-700">
              <ShieldAlert className="h-3.5 w-3.5 shrink-0" aria-hidden="true" /> {r}
            </li>
          ))}
        </ul>
      );
    case "email":
      return (
        <div className="space-y-2 rounded-xl border border-slate-100 bg-slate-50 p-4 text-sm text-slate-600">
          <p className="font-medium text-slate-800">Subject: Recap — Product Sync</p>
          <p>Hi team, quick recap of today&apos;s call — three action items, one open risk. Full details in IntelMeet.</p>
        </div>
      );
  }
}

export default function ProductPreview() {
  const [active, setActive] = useState<TabId>("summary");

  return (
    <section className="bg-slate-50/60 py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading
          eyebrow="Inside the workspace"
          title="One workspace per meeting, every layer already extracted"
          description="No re-reading transcripts. Every tab is generated the moment the upload finishes."
        />

        <div className="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_20px_60px_-20px_rgba(15,23,42,0.15)]">
          <div className="flex flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="shrink-0 border-b border-slate-200 bg-slate-900 p-4 md:w-56 md:border-b-0 md:border-r">
              <button
                type="button"
                className="mb-4 flex w-full items-center justify-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-white/15"
              >
                <Upload className="h-3.5 w-3.5" aria-hidden="true" /> Upload Meeting
              </button>
              <ul className="space-y-1">
                {MEETINGS.map((m, i) => (
                  <li
                    key={m}
                    className={`truncate rounded-lg px-3 py-2 text-xs ${
                      i === 0 ? "bg-white/15 text-white" : "text-white/50"
                    }`}
                  >
                    {m}
                  </li>
                ))}
              </ul>
            </aside>

            {/* Content */}
            <div className="flex-1 p-6">
              <div role="tablist" aria-label="Meeting workspace preview" className="mb-5 flex flex-wrap gap-1 border-b border-slate-100 pb-3">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    role="tab"
                    type="button"
                    aria-selected={active === tab.id}
                    onClick={() => setActive(tab.id)}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                      active === tab.id ? "bg-slate-900 text-white" : "text-slate-500 hover:bg-slate-100"
                    }`}
                  >
                    <tab.icon className="h-3.5 w-3.5" aria-hidden="true" />
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="min-h-[160px]">
                <TabContent tab={active} />
              </div>
            </div>
          </div>

          {/* Footer strip: tiny bar chart, purely decorative/illustrative */}
          <div className="flex items-end gap-1.5 border-t border-slate-100 bg-white px-6 py-4">
            <span className="mr-3 text-[10px] font-medium uppercase tracking-wide text-slate-400">
              Meetings processed / week
            </span>
            {[6, 9, 7, 12, 15, 11, 18].map((h, i) => (
              <span
                key={i}
                className="w-4 rounded-t-sm bg-blue-100 transition-colors hover:bg-blue-300"
                style={{ height: `${h * 2}px` }}
              />
            ))}
          </div>
        </div>
      </Container>
    </section>
  );
}
