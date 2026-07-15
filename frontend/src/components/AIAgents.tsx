import type { ComponentType } from "react";
import { Sparkles, ListChecks, GitCommitHorizontal, ShieldAlert, Mail, Search, BrainCircuit, LineChart } from "lucide-react";
import { Container, SectionHeading, Card, StatusBadge, Reveal, type StatusKind } from "./shared";

type Agent = {
  icon: ComponentType<{ className?: string }>;
  name: string;
  description: string;
  status: StatusKind;
};

const AGENTS: Agent[] = [
  { icon: Sparkles, name: "Summary Agent", description: "Condenses the transcript into an executive-ready summary.", status: "live" },
  { icon: ListChecks, name: "Action Agent", description: "Extracts commitments with an owner and a deadline.", status: "live" },
  { icon: GitCommitHorizontal, name: "Decision Agent", description: "Separates decisions made from options discussed.", status: "live" },
  { icon: ShieldAlert, name: "Risk Agent", description: "Surfaces blockers and open concerns before they escalate.", status: "live" },
  { icon: Mail, name: "Email Agent", description: "Drafts a follow-up email summarizing outcomes for attendees.", status: "live" },
  { icon: Search, name: "Research Agent", description: "Pulls relevant context from past meetings automatically.", status: "coming-soon" },
  { icon: BrainCircuit, name: "Knowledge Agent", description: "Builds a persistent knowledge graph across your meeting history.", status: "planned" },
  { icon: LineChart, name: "Insights Agent", description: "Surfaces trends and patterns across teams over time.", status: "planned" },
];

export default function AIAgents() {
  return (
    <section className="bg-slate-50/60 py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading
          eyebrow="Multi-agent system"
          title="A dedicated agent for every layer of intelligence"
          description="IntelMeet's LangGraph pipeline routes each transcript through a chain of specialized agents rather than one generic prompt."
        />

        <div className="grid w-full gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {AGENTS.map((agent, i) => (
            <Reveal key={agent.name} delayMs={Math.min(i * 60, 240)}>
              <Card className="flex h-full flex-col gap-4">
                <div className="flex items-start justify-between">
                  <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 transition-transform duration-200 group-hover:rotate-[5deg]">
                    <agent.icon className="h-4.5 w-4.5" aria-hidden="true" />
                  </span>
                  <StatusBadge status={agent.status} />
                </div>
                <div className="flex flex-col gap-1.5">
                  <h3 className="text-sm font-semibold text-slate-900">{agent.name}</h3>
                  <p className="text-sm leading-relaxed text-slate-600">{agent.description}</p>
                </div>
              </Card>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}
