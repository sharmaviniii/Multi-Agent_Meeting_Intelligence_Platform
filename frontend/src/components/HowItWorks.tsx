import { UploadCloud, Layers3, Network, LayoutGrid } from "lucide-react";
import { Container, SectionHeading, Reveal, useReducedMotion } from "./shared";

const STEPS = [
  { icon: UploadCloud, title: "Upload transcript", description: "Drop in a transcript, or a txt, pdf, or docx file." },
  { icon: Layers3, title: "Chunk & index", description: "The transcript is split and indexed for retrieval." },
  { icon: Network, title: "Multi-agent analysis", description: "Summary, action, decision, risk, and email agents run in sequence." },
  { icon: LayoutGrid, title: "Workspace ready", description: "Every result lands in one workspace, tab by tab." },
];

/**
 * Connector between two step cards: a static line (GPU-cheap, always
 * visible) plus an animated dot riding along it. The dot animates via
 * `transform`/`opacity` only — never `left` — so it stays GPU-friendly.
 * Skipped entirely when the user prefers reduced motion.
 */
function Connector() {
  const reduced = useReducedMotion();
  return (
    <div
      aria-hidden="true"
      className="absolute -right-4 top-9 hidden h-px w-8 lg:block"
      style={{ background: "linear-gradient(to right, #cbd5e1, #93c5fd)" }}
    >
      {!reduced && (
        <>
          <span
            className="absolute left-0 top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-blue-600"
            style={{ animation: "intelmeet-travel 2.4s ease-in-out infinite" }}
          />
          <style>{`
            @keyframes intelmeet-travel {
              0%   { transform: translate(0, -50%); opacity: 0; }
              15%  { opacity: 1; }
              85%  { opacity: 1; }
              100% { transform: translate(32px, -50%); opacity: 0; }
            }
          `}</style>
        </>
      )}
    </div>
  );
}

export default function HowItWorks() {
  return (
    <section className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading
          eyebrow="How it works"
          title="From raw transcript to organized workspace"
          description="Four steps happen automatically between upload and a finished meeting workspace."
        />

        <ol className="grid w-full gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <Reveal key={step.title} delayMs={i * 200} className="relative">
              <li className="group flex h-full flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-5 transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_12px_24px_-12px_rgba(15,23,42,0.15)]">
                <div className="flex items-center justify-between">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white transition-transform duration-200 group-hover:rotate-[5deg]">
                    <step.icon className="h-4.5 w-4.5" aria-hidden="true" />
                  </span>
                  <span className="text-xs font-medium text-slate-300">0{i + 1}</span>
                </div>
                <h3 className="text-sm font-semibold text-slate-900">{step.title}</h3>
                <p className="text-sm leading-relaxed text-slate-600">{step.description}</p>
              </li>
              {i < STEPS.length - 1 && <Connector />}
            </Reveal>
          ))}
        </ol>
      </Container>
    </section>
  );
}
