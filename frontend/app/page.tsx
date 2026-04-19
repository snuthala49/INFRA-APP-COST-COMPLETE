"use client";
import React, { useState } from "react";
import ProviderCard from "../components/ProviderCard";
import OptionsPanel from "../components/OptionsPanel";
import PricingTable from "../components/PricingTable";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import AboutSection from "../components/AboutSection";
import ContactSection from "../components/ContactSection";
import Footer from "../components/Footer";

interface CostResult {
  provider: string;
  total: number;
  note?: string;
  currency?: string;
  pricing_model?: string;
  instance_count?: number;
  breakdown?: { [k: string]: number };
  assumptions?: string;
  selected_instance?: {
    sku?: string;
    type: string;
    vcpu: number;
    memory_gb: number;
    count?: number;
    price_per_hour?: number;
    price_per_month?: number;
    category?: string;
    description?: string;
  };
}

type ProviderKey = "aws" | "azure" | "gcp";

type TabKey = "product" | "about" | "contact";

export default function Home() {
  const [cpu, setCpu] = useState(2);
  const [ram, setRam] = useState(8);
  const [storage, setStorage] = useState(100);
  const [network, setNetwork] = useState(10);
  const [backup, setBackup] = useState(50);
  const [selectedSkus, setSelectedSkus] = useState<Record<ProviderKey, string | null>>({ aws: null, azure: null, gcp: null });
  const [pricingModel, setPricingModel] = useState<"on_demand" | "reserved_1yr" | "reserved_3yr" | "spot">("on_demand");
  const [instanceCount, setInstanceCount] = useState(1);
  const [storageTypes, setStorageTypes] = useState<Record<ProviderKey, string>>({
    aws: "gp3",
    azure: "standard_ssd",
    gcp: "balanced_pd",
  });

  const [results, setResults] = useState<CostResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<'monthly'|'annual'>('monthly');
  const [activeTab, setActiveTab] = useState<TabKey>("product");
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);
  const periodMultiplier = period === 'monthly' ? 1 : (12 * 0.85);

  const scrollToSection = (tab: TabKey) => {
    setActiveTab(tab);
    const target = document.getElementById(tab);
    if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
  };


  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";
  const pricingModelLabels: Record<string, string> = {
    on_demand: "On-Demand",
    reserved_1yr: "1-Yr Reserved",
    reserved_3yr: "3-Yr Reserved",
    spot: "Spot",
    baseline: "Baseline (TCO)",
  };
  const providerOrder = ["aws", "azure", "gcp", "onprem", "kubernetes"] as const;
  const normalizeProvider = (provider: string) => provider.toLowerCase().replace(/[^a-z]/g, "");
  const providerIndex = (provider: string) => {
    const idx = providerOrder.indexOf(normalizeProvider(provider) as (typeof providerOrder)[number]);
    return idx === -1 ? providerOrder.length : idx;
  };

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cpu,
          ram,
          storage,
          network,
          backup,
          aws_sku: selectedSkus.aws,
          azure_sku: selectedSkus.azure,
          gcp_sku: selectedSkus.gcp,
          pricing_model: pricingModel,
          instance_count: instanceCount,
          aws_storage_type: storageTypes.aws,
          azure_storage_type: storageTypes.azure,
          gcp_storage_type: storageTypes.gcp,
        }),
      });
      if (!res.ok) throw new Error("Backend error");
      const data = await res.json();
      const arr = [data.aws, data.azure, data.gcp, data.onprem, data.kubernetes];
      const normalized = arr.map((r: any) => ({
        ...r,
        total: typeof r.total === "number" ? r.total : Number(r.total || 0),
        currency: r.currency || "USD",
      })).sort((a: any, b: any) => providerIndex(a.provider) - providerIndex(b.provider));
      setResults(normalized);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#0B1220] text-slate-100 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.18),transparent_40%),radial-gradient(circle_at_bottom_left,rgba(34,197,94,0.12),transparent_35%)]">
      <Navbar activeTab={activeTab} onTabClick={scrollToSection} />
      <Hero onTryCalculator={() => scrollToSection("product")} onLearnMore={() => scrollToSection("about")} />

      <section id="product" className="max-w-6xl mx-auto px-4 py-8 scroll-mt-16">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <OptionsPanel
              apiBase={API_BASE}
              storage={storage}
              network={network}
              backup={backup}
              instanceCount={instanceCount}
              pricingModel={pricingModel}
              selectedSkus={selectedSkus}
              storageTypes={storageTypes}
              setStorage={setStorage}
              setNetwork={setNetwork}
              setBackup={setBackup}
              setInstanceCount={setInstanceCount}
              setPricingModel={setPricingModel}
              setSelectedSkus={setSelectedSkus}
              setStorageTypes={setStorageTypes}
              onWorkloadChange={(nextCpu, nextRam) => {
                setCpu(nextCpu);
                setRam(nextRam);
              }}
              period={period}
              setPeriod={setPeriod}
              onCalculate={handleCalculate}
              loading={loading}
            />
          </div>

          <div className="lg:col-span-3 bg-slate-900/65 border border-slate-800 rounded-2xl p-4">
            {results.length > 0 ? (
              <>
                {(() => {
                  const cheapestResult = results.reduce((min, current) =>
                    current.total < min.total ? current : min
                  );
                  const cheapestPricingModel = ["kubernetes", "onprem"].includes(cheapestResult.provider.toLowerCase())
                    ? "baseline"
                    : (cheapestResult.pricing_model || pricingModel);
                  return (
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-slate-400">Cheapest option</div>
                    <div className="text-lg font-semibold text-cyan-300">{cheapestResult.provider} — {new Intl.NumberFormat(undefined, {style:'currency', currency: cheapestResult.currency}).format(cheapestResult.total * periodMultiplier)}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {cheapestResult.selected_instance?.sku || cheapestResult.selected_instance?.type || "Smart Match"} • {pricingModelLabels[cheapestPricingModel]}
                    </div>
                  </div>
                  <div className="text-sm text-slate-400">Comparisons: {results.length}</div>
                </div>
                  );
                })()}

                <PricingTable results={results} multiplier={periodMultiplier} period={period} />

                <div className="mt-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-slate-300">Provider Details</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={scrollLeft}
                        className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 shadow-md hover:shadow-lg flex items-center justify-center transition-all hover:scale-110 text-slate-200"
                        aria-label="Scroll left"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                      <button
                        onClick={scrollRight}
                        className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 shadow-md hover:shadow-lg flex items-center justify-center transition-all hover:scale-110 text-slate-200"
                        aria-label="Scroll right"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 18l6-6-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div className="relative">
                    <div
                      ref={scrollContainerRef}
                      className="flex gap-3 overflow-x-auto py-2 px-1 scroll-smooth snap-x snap-mandatory"
                      style={{
                        scrollbarWidth: 'none',
                        msOverflowStyle: 'none',
                        WebkitOverflowScrolling: 'touch'
                      }}
                    >
                      {results.map((r, idx) => (
                        <div key={idx} className="flex-shrink-0 basis-full sm:basis-1/2 snap-start">
                          <ProviderCard
                            provider={r.provider}
                            total={Math.round(r.total * periodMultiplier * 100) / 100}
                            currency={r.currency}
                            breakdown={r.breakdown}
                            cheapest={r.total === Math.min(...results.map((x) => x.total))}
                            assumptions={r.assumptions}
                            selected_instance={r.selected_instance}
                            pricing_model={
                              ["kubernetes", "onprem"].includes(r.provider.toLowerCase())
                                ? "baseline"
                                : (r.pricing_model || pricingModel)
                            }
                            instance_count={r.instance_count || instanceCount}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="text-center mt-3 text-xs text-slate-400 font-medium">
                    ← Swipe or use arrows to see all {results.length} providers →
                  </div>
                </div>
              </>
            ) : (
              <div className="text-sm text-slate-400">No results yet — enter values and press Calculate</div>
            )}
          </div>
        </div>
      </section>

      <AboutSection />
      <ContactSection />
      <Footer />
    </div>
  );
}
