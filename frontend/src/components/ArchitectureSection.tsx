import type { ComponentType } from "react";
import { MonitorSmartphone, Server, Workflow, BrainCircuit, Database, Boxes, LayoutGrid } from "lucide-react";
import { Container, SectionHeading } from "./shared";

type Node = { icon: ComponentType<{ className?: string }>; label: string; caption: string };

const CHAIN: Node[] = [
  { icon: MonitorSmartphone, label: "Frontend", caption: "React + TypeScript" },
  { icon: Server, label: "FastAPI", caption: "REST API layer" },
  { icon: Workflow, label: "LangGraph", caption: "Agent orchestration" },
  { icon: BrainCircuit, label: "AI Models", caption: "OpenAI GPT-4o-mini" },
];

const PERSISTENCE: Node[] = [
  { icon: Database, label: "PostgreSQL", caption: "Structured data" },
  { icon: Boxes, label: "ChromaDB", caption: "Vector retrieval" },
];

function NodeCard({ node }: { node: Node }) {
  return (
    <div className="flex w-full flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 text-center">
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
        <node.icon className="h-4 w-4" aria-hidden="true" />
      </span>
      <span className="text-xs font-semibold text-slate-900">{node.label}</span>
      <span className="text-[10px] text-slate-400">{node.caption}</span>
    </div>
  );
}

function VConnector() {
  return <div aria-hidden="true" className="h-6 w-px bg-slate-200" />;
}

export default function ArchitectureSection() {
  return (
    <section id="architecture" className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading
          eyebrow="Under the hood"
          title="A multi-agent pipeline, not a single prompt"
          description="Every upload flows through the same production request path — no shortcuts, no hidden state."
        />

        <div className="flex w-full max-w-md flex-col items-center">
          {CHAIN.map((node, i) => (
            <div key={node.label} className="flex w-full flex-col items-center">
              <NodeCard node={node} />
              {i < CHAIN.length - 1 && <VConnector />}
            </div>
          ))}

          <VConnector />

          <div className="grid w-full grid-cols-2 gap-4">
            {PERSISTENCE.map((node) => (
              <NodeCard key={node.label} node={node} />
            ))}
          </div>

          <VConnector />

          <div className="flex w-full flex-col items-center gap-2 rounded-xl border border-slate-900 bg-slate-900 px-4 py-3 text-center">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 text-white">
              <LayoutGrid className="h-4 w-4" aria-hidden="true" />
            </span>
            <span className="text-xs font-semibold text-white">Workspace</span>
            <span className="text-[10px] text-white/50">Meeting-ready in your browser</span>
          </div>
        </div>

        <p className="max-w-xl text-center text-sm text-slate-500">
          Backend: FastAPI · SQLAlchemy · Alembic · LangGraph · ChromaDB — 34 backend tests passing on{" "}
          <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-600">main</code>.
        </p>
      </Container>
    </section>
  );
}
