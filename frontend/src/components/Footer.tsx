import { Sparkles } from "lucide-react";
import { Container, GITHUB_URL, LINKEDIN_URL } from "./shared";

const LINKS = [
  { label: "LinkedIn", href: LINKEDIN_URL, external: true },
  { label: "GitHub", href: GITHUB_URL, external: true },
  { label: "Architecture", href: "#architecture" },
  { label: "Privacy", href: "/privacy" },
  { label: "Roadmap", href: "#roadmap" },
];

export default function Footer() {
  return (
    <footer className="border-t border-slate-100 bg-white py-10">
      <Container className="flex flex-col items-center gap-6 sm:flex-row sm:justify-between">
        <a href="#top" className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 text-white">
            <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          </span>
          <span className="text-sm font-semibold text-slate-900">IntelMeet</span>
        </a>

        <nav aria-label="Footer" className="flex flex-wrap items-center justify-center gap-6">
          {LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.external ? "_blank" : undefined}
              rel={link.external ? "noopener noreferrer" : undefined}
              className="text-sm text-slate-500 transition-colors hover:text-slate-900"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <p className="text-xs text-slate-400">Built with FastAPI + React + LangGraph</p>
      </Container>
    </footer>
  );
}
