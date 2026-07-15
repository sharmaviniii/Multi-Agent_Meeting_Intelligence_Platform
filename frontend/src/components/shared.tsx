import { useEffect, useRef, useState, type ReactNode, type ButtonHTMLAttributes, type AnchorHTMLAttributes } from "react";

/**
 * Single source of truth for external links used across the site.
 * TODO: replace with your real GitHub repo and LinkedIn URLs — these
 * are placeholders so the buttons compile, but they don't point
 * anywhere useful yet.
 */
export const GITHUB_URL = "https://github.com/sharmaviniii/Multi-Agent_Meeting_Intelligence_Platform";
export const LINKEDIN_URL = "https://leetcode.com/u/sharmavanshika1310/";
// TODO: point this at wherever the actual app is mounted (could be "/app",
// a separate subdomain like "https://app.intelmeet.dev", or a dev-only URL
// for now) — confirm against your router before shipping.
export const APP_URL = "/app";

/**
 * Shared visual primitives for the IntelMeet marketing site.
 *
 * Design tokens (encoded here so every section stays consistent):
 * - Surface:   white / slate-50
 * - Ink:       slate-900 (headlines), slate-600 (body), slate-500 (muted)
 * - Border:    slate-200
 * - Accent:    blue-600 (the *only* saturated color on the page)
 * - Emphasis:  slate-900 fill (mirrors the product's own black sidebar/buttons)
 * - Radius:    rounded-xl / rounded-2xl
 * - Type:      two weights only — font-normal (body) and font-semibold (headings)
 */

export function Container({ className = "", children }: { className?: string; children: ReactNode }) {
  return <div className={`mx-auto w-full max-w-6xl px-6 ${className}`}>{children}</div>;
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium tracking-wide text-slate-500">
      {children}
    </span>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
}: {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "center" | "left";
}) {
  const alignment = align === "center" ? "text-center items-center mx-auto" : "text-left items-start";
  return (
    <div className={`flex max-w-2xl flex-col gap-4 ${alignment}`}>
      {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
      <h2 className="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">{title}</h2>
      {description && <p className="text-balance text-base leading-relaxed text-slate-600">{description}</p>}
    </div>
  );
}

export function PrimaryButton({
  children,
  className = "",
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & { children: ReactNode }) {
  return (
    <a
      className={`inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-150 hover:scale-[1.02] hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 ${className}`}
      {...props}
    >
      {children}
    </a>
  );
}

export function SecondaryButton({
  children,
  className = "",
  ...props
}: AnchorHTMLAttributes<HTMLAnchorElement> & { children: ReactNode }) {
  return (
    <a
      className={`inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 transition-all duration-150 hover:scale-[1.02] hover:border-slate-300 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 ${className}`}
      {...props}
    >
      {children}
    </a>
  );
}

export function IconButton({
  children,
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) {
  return (
    <button
      className={`inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export type StatusKind = "live" | "coming-soon" | "planned" | "in-development" | "launching-soon";

const STATUS_STYLES: Record<StatusKind, string> = {
  live: "bg-emerald-50 text-emerald-700 border-emerald-200",
  "in-development": "bg-blue-50 text-blue-700 border-blue-200",
  "launching-soon": "bg-blue-50 text-blue-700 border-blue-200",
  "coming-soon": "bg-slate-100 text-slate-600 border-slate-200",
  planned: "bg-slate-100 text-slate-500 border-slate-200",
};

const STATUS_LABEL: Record<StatusKind, string> = {
  live: "Live",
  "in-development": "In development",
  "launching-soon": "Launching soon",
  "coming-soon": "Coming soon",
  planned: "Planned",
};

export function StatusBadge({ status }: { status: StatusKind }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {status === "live" && <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />}
      {STATUS_LABEL[status]}
    </span>
  );
}

export function Card({ className = "", children }: { className?: string; children: ReactNode }) {
  return (
    <div
      className={`group rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_1px_2px_rgba(15,23,42,0.04)] transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_12px_24px_-12px_rgba(15,23,42,0.15)] ${className}`}
    >
      {children}
    </div>
  );
}

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** Live-updating reduced-motion flag, for gating custom keyframe animations. */
export function useReducedMotion() {
  const [reduced, setReduced] = useState(prefersReducedMotion());

  useEffect(() => {
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => setReduced(mql.matches);
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return reduced;
}

/**
 * Fades + lifts children in once they scroll into view. Falls back to
 * showing content immediately when the user prefers reduced motion.
 * Disconnects its observer on unmount and after the first reveal.
 */
export function Reveal({
  children,
  delayMs = 0,
  className = "",
}: {
  children: ReactNode;
  delayMs?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (prefersReducedMotion()) {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setVisible(true);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.15 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ transitionDelay: visible ? `${delayMs}ms` : "0ms" }}
      className={`transition duration-700 ease-out ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"} ${className}`}
    >
      {children}
    </div>
  );
}

/**
 * Types out a sequence of `speaker: text` lines one character at a time,
 * holds briefly at the end of each line, then advances — looping back to
 * the first line after a longer pause. Every timer is tracked and cleared
 * on unmount or when inputs change, and the whole effect is a no-op (just
 * shows the first line statically) when the user prefers reduced motion.
 */
export type TranscriptTurn = { speaker: string; text: string };

export function useLoopingTypewriter(
  lines: TranscriptTurn[],
  opts?: { typeSpeedMs?: number; holdMs?: number; restartDelayMs?: number }
) {
  const { typeSpeedMs = 32, holdMs = 1200, restartDelayMs = 2600 } = opts ?? {};
  const [output, setOutput] = useState("");
  const reduced = useReducedMotion();

  useEffect(() => {
    if (lines.length === 0) return;

    if (reduced) {
      setOutput(`${lines[0].speaker}: ${lines[0].text}`);
      return;
    }

    let cancelled = false;
    const timers: number[] = [];
    const schedule = (fn: () => void, ms: number) => {
      const id = window.setTimeout(() => {
        if (!cancelled) fn();
      }, ms);
      timers.push(id);
    };

    function typeChar(lineIndex: number, charIndex: number) {
      const full = `${lines[lineIndex].speaker}: ${lines[lineIndex].text}`;
      setOutput(full.slice(0, charIndex));

      if (charIndex < full.length) {
        schedule(() => typeChar(lineIndex, charIndex + 1), typeSpeedMs);
        return;
      }

      // Line finished — hold, then clear and move to the next (or loop).
      schedule(() => {
        const nextIndex = (lineIndex + 1) % lines.length;
        const pause = nextIndex === 0 ? restartDelayMs : typeSpeedMs;
        setOutput("");
        schedule(() => typeChar(nextIndex, 1), pause);
      }, holdMs);
    }

    schedule(() => typeChar(0, 1), typeSpeedMs);

    return () => {
      cancelled = true;
      timers.forEach((id) => window.clearTimeout(id));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lines, typeSpeedMs, holdMs, restartDelayMs, reduced]);

  return output;
}
