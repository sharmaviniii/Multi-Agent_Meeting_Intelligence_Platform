import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, FileText, Mail, ListChecks } from "lucide-react";
import { Container, PrimaryButton, SecondaryButton, Eyebrow, useLoopingTypewriter, APP_URL, type TranscriptTurn } from "./shared";

const TRANSCRIPT_TURNS: TranscriptTurn[] = [
  { speaker: "Alice", text: "Let's finalize the deployment..." },
  { speaker: "Bob", text: "I'll complete the API integration..." },
  { speaker: "Charlie", text: "QA signoff by Wednesday..." },
];

function TranscriptTypewriter() {
  const output = useLoopingTypewriter(TRANSCRIPT_TURNS);
  return (
    <p className="min-h-[2.2em] font-mono text-[11px] leading-snug text-slate-500">
      {output}
      <span className="ml-0.5 motion-safe:animate-pulse">▍</span>
    </p>
  );
}

export default function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const reveal = (delayMs: number) => {
    void delayMs;
    return `motion-safe:transition motion-safe:duration-700 motion-safe:ease-out ${
      mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-3"
    }`;
  };

  return (
    <section id="top" className="relative overflow-hidden bg-white pb-20 pt-16 sm:pb-28 sm:pt-24">
      {/* faint grid, purely textural, no gradient */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]"
      />

      <Container className="grid items-center gap-16 lg:grid-cols-[1.05fr_1fr]">
        <div className="flex flex-col items-start gap-6">
          <div style={{ transitionDelay: "0ms" }} className={reveal(0)}>
            <Eyebrow>Meeting-first workspace</Eyebrow>
          </div>

          <h1
            style={{ transitionDelay: "60ms" }}
            className={`text-balance text-4xl font-semibold leading-[1.1] tracking-tight text-slate-900 sm:text-5xl lg:text-[3.25rem] ${reveal(60)}`}
          >
            Turn every meeting into actionable intelligence
          </h1>

          <p
            style={{ transitionDelay: "120ms" }}
            className={`max-w-lg text-balance text-base leading-relaxed text-slate-600 sm:text-lg ${reveal(120)}`}
          >
            IntelMeet automatically transforms meeting transcripts into executive summaries, action items,
            decisions, risks, and follow-up emails in seconds.
          </p>

          <div style={{ transitionDelay: "180ms" }} className={`flex flex-wrap items-center gap-3 ${reveal(180)}`}>
            <PrimaryButton href={APP_URL}>
              Try IntelMeet
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </PrimaryButton>
            <SecondaryButton href="#architecture">View Architecture</SecondaryButton>
          </div>

          <p style={{ transitionDelay: "220ms" }} className={`text-xs text-slate-400 ${reveal(220)}`}>
            Built in public · Public beta launching soon
          </p>
        </div>

        {/* Product frame with floating intelligence cards */}
        <div className="relative">
          <div
            aria-hidden="true"
            className="absolute left-1/2 top-1/2 -z-10 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-100/50 blur-3xl"
          />
          <div
            style={{ transitionDelay: "100ms" }}
            className={`overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-[0_20px_60px_-15px_rgba(15,23,42,0.15)] ${reveal(100)}`}
          >
            <div className="flex items-center gap-1.5 border-b border-slate-200 bg-slate-50 px-4 py-3">
              <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
              <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
              <span className="h-2.5 w-2.5 rounded-full bg-slate-200" />
              <span className="ml-3 text-xs text-slate-400">workspace/intelmeet-demo</span>
            </div>
            <div className="flex">
              <div className="hidden w-36 shrink-0 border-r border-slate-200 bg-slate-900 p-3 sm:block">
                <div className="mb-4 h-2 w-16 rounded-full bg-white/20" />
                <div className="space-y-2">
                  <div className="h-2 w-full rounded-full bg-white/25" />
                  <div className="h-2 w-3/4 rounded-full bg-white/10" />
                  <div className="h-2 w-5/6 rounded-full bg-white/10" />
                </div>
              </div>
              <div className="flex-1 space-y-3 p-5">
                <div className="h-3 w-1/3 rounded-full bg-slate-200" />
                <div className="h-2 w-full rounded-full bg-slate-100" />
                <div className="h-2 w-11/12 rounded-full bg-slate-100" />
                <div className="h-2 w-4/5 rounded-full bg-slate-100" />
                <div className="mt-4 h-24 rounded-xl border border-slate-100 bg-slate-50" />
              </div>
            </div>
          </div>

          {/* Floating cards */}
          <div
            style={{ transitionDelay: "320ms" }}
            className={`absolute -left-6 -top-6 w-48 rounded-xl border border-slate-200 bg-white p-3 shadow-lg motion-safe:hover:-translate-y-0.5 ${reveal(320)}`}
          >
            <div className="mb-2 flex items-center gap-1.5 text-slate-400">
              <FileText className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="text-[10px] font-medium uppercase tracking-wide">Transcript</span>
            </div>
            <TranscriptTypewriter />
          </div>

          <div
            style={{ transitionDelay: "420ms" }}
            className={`absolute -right-4 top-10 w-48 rounded-xl border border-slate-200 bg-white p-3 shadow-lg motion-safe:hover:-translate-y-0.5 ${reveal(420)}`}
          >
            <div className="mb-2 flex items-center gap-1.5 text-blue-600">
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="text-[10px] font-medium uppercase tracking-wide">Executive summary</span>
            </div>
            <p className="text-[11px] leading-snug text-slate-500">
              Team aligned on Q3 launch date; two blockers flagged for follow-up.
            </p>
          </div>

          <div
            style={{ transitionDelay: "520ms" }}
            className={`absolute -bottom-6 left-6 w-52 rounded-xl border border-slate-200 bg-white p-3 shadow-lg motion-safe:hover:-translate-y-0.5 ${reveal(520)}`}
          >
            <div className="mb-2 flex items-center gap-1.5 text-slate-400">
              <ListChecks className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="text-[10px] font-medium uppercase tracking-wide">Action items</span>
            </div>
            <ul className="space-y-1 text-[11px] text-slate-500">
              <li className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-blue-600" /> Ship pricing page draft
              </li>
              <li className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-blue-600" /> Confirm vendor SLA
              </li>
            </ul>
          </div>

          <div
            style={{ transitionDelay: "600ms" }}
            className={`absolute -right-6 -bottom-8 w-40 rounded-xl border border-slate-200 bg-white p-3 shadow-lg motion-safe:hover:-translate-y-0.5 ${reveal(600)}`}
          >
            <div className="mb-2 flex items-center gap-1.5 text-slate-400">
              <Mail className="h-3.5 w-3.5" aria-hidden="true" />
              <span className="text-[10px] font-medium uppercase tracking-wide">Follow-up email</span>
            </div>
            <div className="space-y-1.5">
              <div className="h-1.5 w-full rounded-full bg-slate-100" />
              <div className="h-1.5 w-2/3 rounded-full bg-slate-100" />
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
