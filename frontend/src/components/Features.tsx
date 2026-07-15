import type { ComponentType } from "react";
import {
  FileText,
  Sparkles,
  ListChecks,
  GitCommitHorizontal,
  ShieldAlert,
  Mail,
  Search,
  LayoutGrid,
} from "lucide-react";
import { Container, SectionHeading, Card, Reveal } from "./shared";

type Feature = {
  icon: ComponentType<{ className?: string }>;
  title: string;
  description: string;
  preview: string;
};

const FEATURES: Feature[] = [
  {
    icon: FileText,
    title: "Meeting transcript",
    description: "Clean, speaker-attributed transcripts generated automatically from your uploaded recording or text.",
    preview: "Asha: We need the demo ready by Friday.",
  },
  {
    icon: Sparkles,
    title: "Executive summary",
    description: "A concise, readable summary of what was discussed — written for people who weren't in the room.",
    preview: "Team aligned on scope; two decisions pending sign-off.",
  },
  {
    icon: ListChecks,
    title: "Action items",
    description: "Every commitment extracted with an owner and a deadline, ready to hand off or track.",
    preview: "Rahul — finish the API — due Fri",
  },
  {
    icon: GitCommitHorizontal,
    title: "Decision extraction",
    description: "The calls that were actually made, separated cleanly from options that were only discussed.",
    preview: "Decision: ship v1 without SSO",
  },
  {
    icon: ShieldAlert,
    title: "Risk detection",
    description: "Flags blockers, dependencies, and open concerns before they quietly become someone's problem.",
    preview: "Risk: vendor SLA unconfirmed",
  },
  {
    icon: Mail,
    title: "Email draft",
    description: "A ready-to-send follow-up email summarizing outcomes and next steps for every attendee.",
    preview: "Subject: Recap — Product Sync",
  },
  {
    icon: Search,
    title: "Semantic search",
    description: "Ask questions across your meeting history and retrieve grounded answers, not just keyword matches.",
    preview: "\u201cWho owns the vendor SLA?\u201d",
  },
  {
    icon: LayoutGrid,
    title: "AI workspace",
    description: "Transcript, summary, actions, decisions, risks, and email — organized in one workspace per meeting.",
    preview: "6 tabs · 1 meeting",
  },
];

export default function Features() {
  return (
    <section id="features" className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading
          eyebrow="Capabilities"
          title="Everything a meeting produces, structured automatically"
          description="IntelMeet reads the transcript once and extracts every layer of intelligence your team actually needs afterward."
        />

        <div className="grid w-full gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature, i) => (
            <Reveal key={feature.title} delayMs={Math.min(i * 60, 240)}>
              <Card className="flex h-full flex-col gap-4">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 transition-transform duration-200 group-hover:rotate-[5deg]">
                  <feature.icon className="h-4.5 w-4.5" aria-hidden="true" />
                </span>
                <div className="flex flex-col gap-1.5">
                  <h3 className="text-sm font-semibold text-slate-900">{feature.title}</h3>
                  <p className="text-sm leading-relaxed text-slate-600">{feature.description}</p>
                </div>
                <div className="mt-auto rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-500">
                  {feature.preview}
                </div>
              </Card>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  );
}
