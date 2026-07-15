import { useEffect, useRef, useState } from "react";
import { X, Check } from "lucide-react";
import { Container, Reveal, useReducedMotion } from "./shared";

const COMPARISON: { without: string; with: string }[] = [
  { without: "Notes scattered", with: "Centralized meeting workspace" },
  { without: "Manual follow-up", with: "AI-generated follow-up email" },
  { without: "Missed action items", with: "Action owners extracted" },
  { without: "Decisions forgotten", with: "Decision tracking" },
  { without: "Risks overlooked", with: "Risk detection" },
  { without: "Hard to search", with: "Semantic search" },
];


const STATS = [
  { value: "5", label: "AI Agents" },
  { value: "40+", label: "Backend Tests" },
  { value: "7", label: "REST APIs" },
];

function AnimatedStat({ value, label }: { value: string; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const match = value.match(/^(\d+)(.*)$/);
  const target = match ? parseInt(match[1], 10) : 0;
  const suffix = match ? match[2] : "";
  const [display, setDisplay] = useState(reduced ? target : 0);

  useEffect(() => {
    const node = ref.current;
    if (!node || reduced) return;

    let frameId: number | null = null;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          observer.disconnect();
          const start = performance.now();
          const duration = 900;
          const tick = (now: number) => {
            const progress = Math.min((now - start) / duration, 1);
            setDisplay(Math.round(progress * target));
            if (progress < 1) frameId = requestAnimationFrame(tick);
          };
          frameId = requestAnimationFrame(tick);
        });
      },
      { threshold: 0.4 }
    );
    observer.observe(node);

    return () => {
      observer.disconnect();
      if (frameId !== null) cancelAnimationFrame(frameId);
    };
  }, [target, reduced]);

  return (
    <div
      ref={ref}
      className="flex flex-col items-center gap-1 rounded-2xl border border-slate-200 bg-white py-6 text-center transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_12px_24px_-12px_rgba(15,23,42,0.15)]"
    >
      <span className="text-3xl font-semibold tracking-tight text-slate-900">
        {display}
        {suffix}
      </span>
      <span className="text-xs font-medium text-slate-500">{label}</span>
    </div>
  );
}

export default function WhyIntelMeet() {
  return (
    <section className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <div className="flex max-w-2xl flex-col items-center gap-4 text-center">
          <h2 className="text-balance text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
            Stop turning meetings into forgotten notes
          </h2>
          <p className="text-balance text-base leading-relaxed text-slate-600">
            IntelMeet automatically converts conversations into structured business intelligence.
          </p>
        </div>

        <div className="grid w-full gap-6 lg:grid-cols-2">
          <Reveal className="rounded-2xl border border-slate-200 bg-slate-50 p-6 sm:p-8">
            <h3 className="mb-5 text-sm font-semibold uppercase tracking-wide text-slate-400">Without IntelMeet</h3>
            <ul className="space-y-3.5">
              {COMPARISON.map((row) => (
                <li key={row.without} className="flex items-start gap-3 text-sm text-slate-500">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-500">
                    <X className="h-3 w-3" aria-hidden="true" />
                  </span>
                  {row.without}
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal delayMs={120} className="rounded-2xl border border-slate-900 bg-slate-900 p-6 sm:p-8">
            <h3 className="mb-5 text-sm font-semibold uppercase tracking-wide text-white/50">With IntelMeet</h3>
            <ul className="space-y-3.5">
              {COMPARISON.map((row) => (
                <li key={row.with} className="flex items-start gap-3 text-sm text-white/90">
                  <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
                    <Check className="h-3 w-3" aria-hidden="true" />
                  </span>
                  {row.with}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>

        <div className="grid w-full grid-cols-1 gap-4 sm:grid-cols-3">
          {STATS.map((stat) => (
            <AnimatedStat key={stat.label} value={stat.value} label={stat.label} />
          ))}
        </div>
      </Container>
    </section>
  );
}
