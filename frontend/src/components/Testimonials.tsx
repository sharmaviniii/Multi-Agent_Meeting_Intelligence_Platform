import { Container, SectionHeading, Card } from "./shared";

const QUOTES = [
  {
    role: "Engineering Manager",
    quote: "The action-item extraction alone saves our team the fifteen minutes we used to spend writing recap notes after every sync.",
  },
  {
    role: "Product Lead",
    quote: "Having decisions and risks separated automatically means nothing discussed in a meeting quietly gets lost by Friday.",
  },
  {
    role: "Startup Founder",
    quote: "We used to skip follow-up emails entirely. Now they draft themselves in the time it takes to close the laptop.",
  },
  {
    role: "Operations Team",
    quote: "Semantic search across past meetings replaced a shared doc nobody kept up to date.",
  },
];

export default function Testimonials() {
  return (
    <section className="bg-white py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-10">
        <SectionHeading eyebrow="Product preview" title="What early workflows look like" />
        <p className="-mt-6 text-xs text-slate-400">
          Illustrative quotes based on target workflows, shown ahead of public launch.
        </p>

        <div className="grid w-full gap-5 sm:grid-cols-2">
          {QUOTES.map((t) => (
            <Card key={t.role} className="flex flex-col gap-4">
              <p className="text-sm leading-relaxed text-slate-700">&ldquo;{t.quote}&rdquo;</p>
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{t.role}</span>
            </Card>
          ))}
        </div>
      </Container>
    </section>
  );
}
