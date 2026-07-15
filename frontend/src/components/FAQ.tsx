import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Container, SectionHeading } from "./shared";

const QUESTIONS = [
  {
    q: "What file formats are supported?",
    a: "IntelMeet accepts raw text, .txt, .pdf, and .docx transcripts. Audio and video ingestion are on the roadmap.",
  },
  {
    q: "How is data stored?",
    a: "Structured meeting data is stored in PostgreSQL. Transcript embeddings for semantic search are stored in ChromaDB.",
  },
  {
    q: "Is there a free plan?",
    a: "Yes — the Free plan covers a limited number of meetings per month, with no card required to try it.",
  },
  {
    q: "Does IntelMeet use AI?",
    a: "Yes. A LangGraph-orchestrated pipeline of specialized agents processes every transcript through OpenAI models.",
  },
  {
    q: "Can teams collaborate?",
    a: "Shared workspaces and team roles (RBAC) are in active development and are not yet available in the current build.",
  },
  {
    q: "Is my data secure?",
    a: "Protected endpoints require authenticated access, and CORS is restricted to approved origins — no wildcard access.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading eyebrow="FAQ" title="Common questions" />

        <div className="w-full max-w-2xl divide-y divide-slate-200 rounded-2xl border border-slate-200">
          {QUESTIONS.map((item, i) => {
            const expanded = open === i;
            return (
              <div key={item.q}>
                <h3>
                  <button
                    type="button"
                    aria-expanded={expanded}
                    aria-controls={`faq-panel-${i}`}
                    onClick={() => setOpen(expanded ? null : i)}
                    className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left text-sm font-medium text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-slate-900"
                  >
                    {item.q}
                    <ChevronDown
                      aria-hidden="true"
                      className={`h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
                    />
                  </button>
                </h3>
                {expanded && (
                  <div id={`faq-panel-${i}`} className="px-5 pb-4 text-sm leading-relaxed text-slate-600">
                    {item.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
