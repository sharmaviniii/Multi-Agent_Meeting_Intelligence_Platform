import { Sparkles, ArrowLeft } from "lucide-react";

/**
 * App-wide 404 page. Deliberately self-contained (no imports from
 * features/landing) since this route applies to the whole app, not
 * just the marketing site. Wire it into your router as the catch-all:
 *
 *   import NotFound from "@/app/NotFound";
 *   <Route path="*" element={<NotFound />} />
 */
export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-white px-6 text-center">
      <a href="/" className="flex items-center gap-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
          <Sparkles className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-sm font-semibold tracking-tight text-slate-900">IntelMeet</span>
      </a>

      <div className="flex flex-col items-center gap-3">
        <span className="text-6xl font-semibold tracking-tight text-slate-200">404</span>
        <h1 className="text-xl font-semibold text-slate-900">This page doesn&apos;t exist</h1>
        <p className="max-w-sm text-sm leading-relaxed text-slate-500">
          The meeting, workspace, or page you&apos;re looking for isn&apos;t here. It may have moved, or the link
          might be off.
        </p>
      </div>

      <a
        href="/"
        className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition-all duration-150 hover:scale-[1.02] hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Back to home
      </a>
    </main>
  );
}
