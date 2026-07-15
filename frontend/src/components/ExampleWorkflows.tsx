import type { ComponentType } from "react";
import { Users, Handshake, ListTodo, Siren } from "lucide-react";
import { Container, SectionHeading, Card, Reveal } from "./shared";

type Workflow = {
  icon: ComponentType<{ className?: string }>;
  title: string;
  scenario: string;
  outcome: string;
};

const WORKFLOWS: Workflow[] = [
  {
    icon: Users,
    title: "Weekly product sync",
    scenario: "45-minute sync, 6 attendees, no dedicated notetaker.",
    outcome: "3 action items assigned, 1 risk flagged, follow-up email drafted in under a minute.",
  },
  {
    icon: Handshake,
    title: "Vendor negotiation call",
    scenario: "External call — terms discussed, one decision pending.",
    outcome: "The decision and its rationale are captured without anyone writing a recap afterward.",
  },
  {
    icon: ListTodo,
    title: "Sprint planning",
    scenario: "Full backlog review across a five-person team.",
    outcome: "Commitments extracted with owners and due dates, ready to paste into the tracker.",
  },
  {
    icon: Siren,
    title: "Incident review",
    scenario: "Cross-team call after a production issue.",
    outcome: "Root cause and mitigation steps become searchable ahead of the next related meeting.",
  },
];

export default function ExampleWorkflows() {
  return (
    <section className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-10">
        <SectionHeading eyebrow="Example workflows" title="What a processed meeting actually looks like" description="Illustrative scenarios built from IntelMeet's real extraction pipeline — not customer quotes." />

        <div className="grid w-full gap-5 sm:grid-cols-2">
          {WORKFLOWS.map((w, i) => (
            <Reveal key={w.title} delayMs={Math.min(i * 80, 240)}>
              <Card className="flex h-full flex-col gap-4">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 transition-transform duration-200 group-hover:rotate-[5deg]">
                  <w.icon className="h-4.5 w-4.5" aria-hidden="true" />
                </span>
                <div className="flex flex-col gap-2">
                  <h3 className="text-sm font-semibold text-slate-900">{w.title}</h3>
                  <p className="text-sm leading-relaxed text-slate-500">
                    <span className="font-medium text-slate-600">Scenario — </span>
                    {w.scenario}
                  </p>
                  <p className="text-sm leading-relaxed text-slate-700">
                    <span className="font-medium text-slate-600">Outcome — </span>
                    {w.outcome}
                  </p>
                </div>
              </Card>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}
