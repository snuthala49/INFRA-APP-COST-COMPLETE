"use client";
import React, { useState } from "react";
import InputField from "../components/InputField";
import DarkModeToggle from "../components/DarkModeToggle";
import ProviderCard from "../components/ProviderCard";

interface CostResult {
  provider: string;
  total: number;
  note?: string;
  currency?: string;
  breakdown?: { [k: string]: number };
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
          <div className="flex items-center gap-2">
            <button data-testid="mode-toggle" onClick={() => setTileMode(tileMode === 'illustration' ? 'photo' : 'illustration')} className="px-3 py-1 rounded bg-white/8 hover:bg-white/12">{tileMode === 'illustration' ? 'Photo tiles' : 'Illustration tiles'}</button>
            <div className="infra-illustration" aria-hidden>
              <img src="/assets/infra-illustration.svg" alt="infrastructure illustration" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 calculator-panel">
          <h2 className="text-lg font-medium mb-3">Calculator</h2>
          <div className="grid grid-cols-1 gap-3">
            <InputField label="CPU (vCPUs)" value={cpu} onChange={setCpu} />
            <InputField label="RAM (GB)" value={ram} onChange={setRam} />
            <InputField label="Storage (GB)" value={storage} onChange={setStorage} />
            <InputField label="Network (Mbps)" value={network} onChange={setNetwork} />
            <InputField label="Backup (GB)" value={backup} onChange={setBackup} />
          </div>
          <button
            onClick={handleCalculate}
            data-testid="calculate-btn"
            className="mt-4 w-full btn-primary py-3 text-lg"
          >
            {loading ? "Calculating..." : "Calculate"}
          </button>
        </div>

        <div className="md:col-span-2">
          {results.length > 0 ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-500">Cheapest option</div>
                  <div className="text-lg font-semibold">{results[0].provider} — {new Intl.NumberFormat(undefined, {style:'currency', currency: results[0].currency}).format(results[0].total)}</div>
                </div>
                <div className="text-sm text-gray-400">Comparisons: {results.length}</div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {results.map((r, idx) => (
                  <div key={idx}>
                    <ProviderCard provider={r.provider} total={r.total} currency={r.currency} breakdown={r.breakdown} cheapest={idx === 0} imageMode={tileMode} />
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">No results yet — enter values and press Calculate</div>
          )}
        </div>
      </div>

      {results.length > 0 && (
        <div className="mt-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500">Cheapest option</div>
                <div className="text-lg font-semibold">{results[0].provider} — {new Intl.NumberFormat(undefined, {style:'currency', currency: results[0].currency}).format(results[0].total)}</div>
            </div>
            <div className="text-sm text-gray-400">Comparisons: {results.length}</div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((r, idx) => (
              <div key={idx}>
                <ProviderCard provider={r.provider} total={r.total} currency={r.currency} breakdown={r.breakdown} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
