import { useState, type FormEvent } from "react";
import { Container, SectionHeading, Card, StatusBadge, type StatusKind } from "./shared";

const ITEMS: { title: string; status: StatusKind }[] = [
  { title: "Authentication", status: "in-development" },
  { title: "Workspaces", status: "in-development" },
  { title: "Teams", status: "launching-soon" },
  { title: "AI streaming", status: "launching-soon" },
  { title: "Live collaboration", status: "planned" },
  { title: "Enterprise search", status: "planned" },
  { title: "Billing", status: "planned" },
  { title: "Knowledge graph", status: "planned" },
  { title: "Redis queue", status: "planned" },
  { title: "Background jobs", status: "planned" },
  { title: "Vector memory", status: "planned" },
];

export default function Roadmap() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    // Frontend-only: no backend endpoint exists for the waitlist yet.
    if (email.trim()) setSubmitted(true);
  }

  return (
    <section id="roadmap" className="bg-slate-50/60 py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading eyebrow="Roadmap" title="What's coming next" description="IntelMeet ships in small, working increments — here's the honest state of what's live, in progress, and planned." />

        <div className="grid w-full gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ITEMS.map((item) => (
            <Card key={item.title} className="flex items-center justify-between gap-3 py-4">
              <span className="text-sm font-medium text-slate-800">{item.title}</span>
              <StatusBadge status={item.status} />
            </Card>
          ))}
        </div>

        <div id="waitlist" className="w-full rounded-2xl border border-slate-200 bg-slate-900 px-6 py-10 text-center sm:px-10">
          <StatusBadge status="launching-soon" />
          <h3 className="mt-4 text-2xl font-semibold tracking-tight text-white">IntelMeet public beta</h3>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-white/60">
            Join the waitlist to get early access as new capabilities ship.
          </p>

          {submitted ? (
            <p className="mt-6 text-sm font-medium text-white">You&apos;re on the list — we&apos;ll be in touch.</p>
          ) : (
            <form onSubmit={handleSubmit} className="mx-auto mt-6 flex max-w-sm flex-col gap-3 sm:flex-row">
              <label htmlFor="waitlist-email" className="sr-only">
                Email address
              </label>
              <input
                id="waitlist-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-white/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              />
              <button
                type="submit"
                className="shrink-0 rounded-lg bg-white px-5 py-2.5 text-sm font-medium text-slate-900 transition-colors hover:bg-white/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                Notify me
              </button>
            </form>
          )}
        </div>
      </Container>
    </section>
  );
}
