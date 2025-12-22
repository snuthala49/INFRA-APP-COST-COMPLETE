"use client";
import React, { useState } from "react";
import InputField from "../components/InputField";
import DarkModeToggle from "../components/DarkModeToggle";
import ProviderCard from "../components/ProviderCard";
import OptionsPanel from "../components/OptionsPanel";
import PricingTable from "../components/PricingTable";

interface CostResult {
  provider: string;
  total: number;
  note?: string;
  currency?: string;
  breakdown?: { [k: string]: number };
  selected_instance?: { sku?: string; count?: number; price_per_hour?: number; price_per_month?: number };
}

export default function Home() {
  const [cpu, setCpu] = useState(2);
  const [ram, setRam] = useState(8);
  const [storage, setStorage] = useState(100);
  const [network, setNetwork] = useState(10);
  const [backup, setBackup] = useState(50);

  const [results, setResults] = useState<CostResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [tileMode, setTileMode] = useState<'illustration' | 'photo'>('illustration');
  const [period, setPeriod] = useState<'monthly'|'6mo'|'annual'>('monthly');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5001";

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
      // normalize each result and ensure we always show all providers in a fixed order
      const normalized = arr.map((r: any, i: number) => ({
        ...r,
        provider: r?.provider || ['aws','azure','gcp','kubernetes','onprem'][i],
        total: typeof r?.total === "number" ? r.total : Number(r?.total || 0),
        currency: r?.currency || "USD",
        breakdown: r?.breakdown || {},
      }));
      // sort by total but keep stable order for display in table; we'll produce an ordered display below
      const sorted = [...normalized].sort((a: any, b: any) => a.total - b.total);

      // Create an ordered list for display (fixed provider order) so horizontal scroller shows all providers consistently
      const providerOrder = ['aws','azure','gcp','kubernetes','onprem'];
      const ordered = providerOrder.map((p) => {
        const found = normalized.find((x) => String(x.provider).toLowerCase() === p);
        return found || { provider: p, total: 0, currency: 'USD', breakdown: {} };
      });

      // mark cheapest based on sorted result (if totals >0)
      const cheapestProvider = sorted.length ? sorted[0].provider : null;
      const final = ordered.map((x) => ({ ...x, cheapest: cheapestProvider && String(cheapestProvider).toLowerCase() === String(x.provider).toLowerCase() }));
      setResults(final);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 page-root">
      <div className="site-header mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-cyan-500 text-white shadow-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 7h18v4H3z" fill="currentColor" opacity="0.9"></path><path d="M5 13h14v6H5z" fill="currentColor" opacity="0.7"></path></svg>
          </div>
          <div>
            <div className="site-title">Infrastructure Cost Calculator</div>
            <div className="site-sub">Compare cloud, Kubernetes and on-prem costs instantly</div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <DarkModeToggle />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <OptionsPanel cpu={cpu} ram={ram} storage={storage} network={network} backup={backup} setCpu={setCpu} setRam={setRam} setStorage={setStorage} setNetwork={setNetwork} setBackup={setBackup} period={period} setPeriod={(p) => setPeriod(p as any)} onCalculate={handleCalculate} loading={loading} />
        </div>

        <div className="md:col-span-2">
          {results.length > 0 ? (
            <>
              {/* Comparison table at the top as requested */}
              <PricingTable results={results} multiplier={period === 'monthly' ? 1 : period === '6mo' ? 0.9 : 0.8} />

              <div className="mt-4 mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-500">Cheapest option</div>
                  {(() => {
                    const found = results.find(r => r.cheapest);
                    return found ? <div className="text-lg font-semibold">{found.provider} — {new Intl.NumberFormat(undefined, {style:'currency', currency: found.currency}).format(found.total)}</div> : <div className="text-lg font-semibold">N/A</div>;
                  })()}
                </div>
                <div className="text-sm text-gray-400">Comparisons: {results.length}</div>
              </div>

              {/* Horizontal scroller with all providers at the bottom (with arrows and peek) */}
              <div className="pt-2 relative">
                <Scroller results={results} />
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">No results yet — enter values and press Calculate</div>
          )}
        </div>
      </div>

      {/* Single results area shown above; removed duplicated bottom card list to avoid duplicates */}
    </div>
  );
}

function Scroller({ results }: { results: any[] }) {
  const ref = React.useRef<HTMLDivElement | null>(null);
  const [canLeft, setCanLeft] = React.useState(false);
  const [canRight, setCanRight] = React.useState(false);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => {
      setCanLeft(el.scrollLeft > 8);
      setCanRight(el.scrollWidth - el.clientWidth - el.scrollLeft > 8);
    };
    update();
    el.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      el.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, [results]);

  const doScroll = (dir: 'left'|'right') => {
    const el = ref.current;
    if (!el) return;
    const amount = Math.max(el.clientWidth * 0.6, 280);
    el.scrollBy({ left: dir === 'left' ? -amount : amount, behavior: 'smooth' });
  };

  return (
    <div className="relative">
      <div className={`absolute left-0 top-0 bottom-0 w-12 pointer-events-none bg-gradient-to-r from-white/90 dark:from-black/80`} aria-hidden />
      <div className={`absolute right-0 top-0 bottom-0 w-12 pointer-events-none bg-gradient-to-l from-white/90 dark:from-black/80`} aria-hidden />

      <button aria-label="Scroll left" onClick={() => doScroll('left')} className={`absolute left-2 top-1/2 -translate-y-1/2 z-20 bg-white/90 dark:bg-black/80 rounded-full p-1 shadow-md ${canLeft ? '' : 'opacity-40 pointer-events-none'}`}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </button>

      <div ref={ref} role="list" aria-label="Provider comparisons" tabIndex={0} onKeyDown={(e) => { if (e.key === 'ArrowLeft') doScroll('left'); if (e.key === 'ArrowRight') doScroll('right'); }} className="flex gap-4 overflow-x-auto hide-scrollbar py-2 px-6 sm:px-2 scroll-snap-x">
                  {results.map((r, idx) => (
                    <div key={String(r.provider)} role="listitem" className="min-w-[260px] sm:min-w-[280px] scroll-snap-align-start">
            <ProviderCard provider={r.provider} total={Math.round(r.total * 100) / 100} currency={r.currency} breakdown={r.breakdown} cheapest={r.cheapest} imageMode={'illustration'} selected_instance={r.selected_instance} />
          </div>
        ))}
      </div>

      <button aria-label="Scroll right" onClick={() => doScroll('right')} className={`absolute right-2 top-1/2 -translate-y-1/2 z-20 bg-white/90 dark:bg-black/80 rounded-full p-1 shadow-md ${canRight ? '' : 'opacity-40 pointer-events-none'}`}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </button>
    </div>
  );
}
