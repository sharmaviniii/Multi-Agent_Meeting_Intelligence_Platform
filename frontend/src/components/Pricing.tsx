import { Check } from "lucide-react";
import { Container, SectionHeading, SecondaryButton } from "./shared";

const TIERS = [
  {
    name: "Free",
    price: "$0",
    description: "For trying IntelMeet on a handful of meetings.",
    features: ["Up to 5 meetings / month", "Summary + action items", "7-day history"],
  },
  {
    name: "Pro",
    price: "$—",
    description: "For individuals running meetings every week.",
    features: ["Unlimited meetings", "All 5 AI agents", "Semantic search", "Full history"],
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams that need workspaces, roles, and SSO.",
    features: ["Workspaces & teams", "RBAC & SSO", "Priority support", "Custom retention"],
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="bg-slate-50/60 py-20 sm:py-28">
      <Container className="flex flex-col items-center gap-14">
        <SectionHeading eyebrow="Pricing" title="Plans for when the beta opens" description="Pricing isn't live yet — this reflects the intended structure at launch." />

        <div className="grid w-full gap-6 lg:grid-cols-3">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`flex flex-col gap-6 rounded-2xl border p-6 transition-all duration-200 hover:-translate-y-1 ${
                tier.highlighted ? "border-slate-900 bg-slate-900 text-white hover:shadow-[0_12px_24px_-12px_rgba(15,23,42,0.4)]" : "border-slate-200 bg-white hover:shadow-[0_12px_24px_-12px_rgba(15,23,42,0.15)]"
              }`}
            >
              <div className="flex items-center justify-between">
                <h3 className={`text-sm font-semibold ${tier.highlighted ? "text-white" : "text-slate-900"}`}>{tier.name}</h3>
                <span
                  className={`rounded-full border px-2.5 py-0.5 text-[10px] font-medium ${
                    tier.highlighted ? "border-white/20 bg-white/10 text-white/70" : "border-slate-200 bg-slate-100 text-slate-500"
                  }`}
                >
                  Public beta
                </span>
              </div>

              <div>
                <span className={`text-3xl font-semibold tracking-tight ${tier.highlighted ? "text-white" : "text-slate-900"}`}>
                  {tier.price}
                </span>
                {tier.price.startsWith("$") && tier.price !== "$0" && (
                  <span className={tier.highlighted ? "text-white/50" : "text-slate-400"}> /month</span>
                )}
              </div>

              <p className={`text-sm leading-relaxed ${tier.highlighted ? "text-white/60" : "text-slate-600"}`}>{tier.description}</p>

              <ul className="flex flex-1 flex-col gap-2.5">
                {tier.features.map((f) => (
                  <li key={f} className={`flex items-center gap-2 text-sm ${tier.highlighted ? "text-white/80" : "text-slate-600"}`}>
                    <Check className={`h-3.5 w-3.5 shrink-0 ${tier.highlighted ? "text-white" : "text-blue-600"}`} aria-hidden="true" />
                    {f}
                  </li>
                ))}
              </ul>

              <SecondaryButton
                href="#waitlist"
                className={tier.highlighted ? "border-white/20 bg-white/10 text-white hover:bg-white/15" : ""}
              >
                Coming Soon
              </SecondaryButton>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
