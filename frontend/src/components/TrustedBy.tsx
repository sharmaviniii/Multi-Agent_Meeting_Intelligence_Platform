import { Container } from "./shared";

const STACK = [
  "FastAPI",
  "LangGraph",
  "React",
  "TypeScript",
  "PostgreSQL",
  "ChromaDB",
  "OpenAI",
  "Docker",
  "GitHub Actions",
];

export default function TrustedBy() {
  return (
    <section aria-label="Built with" className="border-y border-slate-100 bg-slate-50/60 py-10">
      <Container>
        <p className="mb-6 text-center text-xs font-medium uppercase tracking-widest text-slate-400">Built with</p>
        <ul className="flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
          {STACK.map((tool) => (
            <li
              key={tool}
              className="text-sm font-medium text-slate-400 grayscale transition-colors duration-150 hover:text-slate-600"
            >
              {tool}
            </li>
          ))}
        </ul>
      </Container>
    </section>
  );
}
