import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import WhyIntelMeet from "./components/WhyIntelMeet";
import TrustedBy from "./components/TrustedBy";
import ProductPreview from "./components/ProductPreview";
import Features from "./components/Features";
import HowItWorks from "./components/HowItWorks";
import AIAgents from "./components/AIAgents";
import ArchitectureSection from "./components/ArchitectureSection";
import Metrics from "./components/Metrics";
import ExampleWorkflows from "./components/ExampleWorkflows";
import Pricing from "./components/Pricing";
import Roadmap from "./components/Roadmap";
import FAQ from "./components/FAQ";
import Footer from "./components/Footer";

/**
 * Public marketing site for IntelMeet.
 *
 * Isolated from the product: this page does not import from
 * meeting-workspace/, upload/, or services/api.ts, and introduces
 * no new routes, API calls, or shared state. Safe to mount at "/"
 * or any standalone marketing route without touching the app shell.
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 antialiased">
      <Navbar />
      <main>
        <Hero />
        <WhyIntelMeet />
        <TrustedBy />
        <ProductPreview />
        <Features />
        <HowItWorks />
        <AIAgents />
        <ArchitectureSection />
        <Metrics />
        <ExampleWorkflows />
        <Pricing />
        <Roadmap />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
}
