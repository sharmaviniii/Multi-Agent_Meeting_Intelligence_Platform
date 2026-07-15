import { Container } from "./shared";

const METRICS = [
  { value: "40+", label: "Automated tests" },
  { value: "7", label: "REST API endpoints" },
  { value: "5", label: "Live AI agents" },
  { value: "React 19", label: "TypeScript frontend" },
  { value: "Docker", label: "Reproducible deploys" },
  { value: "Semantic", label: "ChromaDB search" },
];

export default function Metrics() {
  return (
    <section className="border-y border-slate-100 bg-white py-14">
      <Container>
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-6">
          {METRICS.map((m) => (
            <div key={m.label} className="flex flex-col items-center gap-1 text-center">
              <span className="text-2xl font-semibold tracking-tight text-slate-900">{m.value}</span>
              <span className="text-xs text-slate-500">{m.label}</span>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
