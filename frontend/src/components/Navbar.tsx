import { useEffect, useState } from "react";
import { Menu, Sparkles, X } from "lucide-react";
import { Container, PrimaryButton, GITHUB_URL, APP_URL } from "./shared";

const LINKS = [
  { label: "Features", href: "#features" },
  { label: "Architecture", href: "#architecture" },
  { label: "Pricing", href: "#pricing" },
  { label: "Roadmap", href: "#roadmap" },
  { label: "GitHub", href: GITHUB_URL, external: true },
];

// The demo app is live and reachable — flip to false to fall back to the waitlist CTA.
const APP_IS_LIVE = true;

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 w-full border-b transition-colors duration-200 ${
        scrolled ? "border-slate-200 bg-white/80 backdrop-blur-md" : "border-transparent bg-white/60 backdrop-blur-sm"
      }`}
    >
      <Container className="flex h-16 items-center justify-between">
        <a href="#top" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          </span>
          <span className="text-sm font-semibold tracking-tight text-slate-900">IntelMeet</span>
        </a>

        <nav aria-label="Primary" className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.external ? "_blank" : undefined}
              rel={link.external ? "noopener noreferrer" : undefined}
              className="text-sm font-normal text-slate-600 transition-colors hover:text-slate-900"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:block">
          <PrimaryButton href={APP_IS_LIVE ? APP_URL : "#waitlist"}>
            {APP_IS_LIVE ? "Launch App" : "Coming Soon"}
          </PrimaryButton>
        </div>

        <button
          type="button"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-700 md:hidden"
          onClick={() => setMobileOpen((v) => !v)}
        >
          {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </Container>

      {mobileOpen && (
        <div className="border-t border-slate-200 bg-white md:hidden">
          <Container className="flex flex-col gap-1 py-4">
            {LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                onClick={() => setMobileOpen(false)}
                className="rounded-lg px-3 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
              >
                {link.label}
              </a>
            ))}
            <PrimaryButton href={APP_IS_LIVE ? APP_URL : "#waitlist"} className="mt-2 w-full">
              {APP_IS_LIVE ? "Launch App" : "Coming Soon"}
            </PrimaryButton>
          </Container>
        </div>
      )}
    </header>
  );
}
