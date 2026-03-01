"use client";
import React, { useState } from "react";
import InputField from "../components/InputField";
import ProviderCard from "../components/ProviderCard";
import OptionsPanel from "../components/OptionsPanel";
import PricingTable from "../components/PricingTable";

interface CostResult {
  provider: string;
  total: number;
  note?: string;
  currency?: string;
  breakdown?: { [k: string]: number };
  assumptions?: string;
  selected_instance?: {
    type: string;
    vcpu: number;
    memory_gb: number;
    category?: string;
    description?: string;
  };
}

export default function Home() {
  const [cpu, setCpu] = useState(2);
  const [ram, setRam] = useState(8);
  const [storage, setStorage] = useState(100);
  const [network, setNetwork] = useState(10);
  const [backup, setBackup] = useState(50);

  const [results, setResults] = useState<CostResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [period, setPeriod] = useState<'monthly'|'annual'>('monthly');
  const scrollContainerRef = React.useRef<HTMLDivElement>(null);

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

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cpu, ram, storage, network, backup }),
      });
      if (!res.ok) throw new Error("Backend error");
      const data = await res.json();
      const arr = [data.aws, data.azure, data.gcp, data.kubernetes, data.onprem];
      // normalize and sort by total ascending, also provide currency
      const normalized = arr.map((r: any) => ({
        ...r,
        total: typeof r.total === "number" ? r.total : Number(r.total || 0),
        currency: r.currency || "USD",
      })).sort((a: any, b: any) => a.total - b.total);
      setResults(normalized);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 page-root">
      <div className="site-header mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-cyan-500 text-white shadow-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 7h18v4H3z" fill="currentColor" opacity="0.9"></path><path d="M5 13h14v6H5z" fill="currentColor" opacity="0.7"></path></svg>
          </div>
          <div>
            <div className="site-title">Testing CI CD AUTOMATION final</div>
            <div className="site-sub">Compare cloud, Kubernetes and on-prem costs instantly</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <OptionsPanel cpu={cpu} ram={ram} storage={storage} network={network} backup={backup} setCpu={setCpu} setRam={setRam} setStorage={setStorage} setNetwork={setNetwork} setBackup={setBackup} period={period} setPeriod={setPeriod} onCalculate={handleCalculate} loading={loading} />
        </div>

        <div className="lg:col-span-3">{results.length > 0 ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Cheapest option</div>
                  <div className="text-lg font-semibold text-indigo-700 dark:text-cyan-300">{results[0].provider} — {new Intl.NumberFormat(undefined, {style:'currency', currency: results[0].currency}).format(results[0].total)}</div>
                </div>
                <div className="text-sm text-gray-400">Comparisons: {results.length}</div>
              </div>

              <PricingTable results={results} multiplier={period === 'monthly' ? 1 : 0.85} />

              <div className="mt-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Provider Details</h3>
                  <div className="flex gap-2">
                    <button 
                      onClick={scrollLeft}
                      className="w-8 h-8 rounded-full bg-white dark:bg-gray-800 shadow-md hover:shadow-lg flex items-center justify-center transition-all hover:scale-110 text-gray-700 dark:text-gray-300"
                      aria-label="Scroll left"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </button>
                    <button 
                      onClick={scrollRight}
                      className="w-8 h-8 rounded-full bg-white dark:bg-gray-800 shadow-md hover:shadow-lg flex items-center justify-center transition-all hover:scale-110 text-gray-700 dark:text-gray-300"
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
                        <ProviderCard provider={r.provider} total={Math.round(r.total * 100) / 100} currency={r.currency} breakdown={r.breakdown} cheapest={idx === 0} assumptions={r.assumptions} selected_instance={r.selected_instance} />
                      </div>
                    ))}
                  </div>
                  {/* Gradient hints for overflow */}
                  <div className="pointer-events-none absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-gray-50 dark:from-gray-900 to-transparent opacity-75"></div>
                  <div className="pointer-events-none absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-gray-50 dark:from-gray-900 to-transparent opacity-75"></div>
                </div>
                <div className="text-center mt-3 text-xs text-gray-500 dark:text-gray-400 font-medium">
                  ← Swipe or use arrows to see all {results.length} providers →
                </div>
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500 dark:text-gray-400">No results yet — enter values and press Calculate</div>
          )}
        </div>
      </div>
    </div>
  );
}
