"use client";
import React, { useState } from "react";

interface Props {
  provider: string;
  total: number | string;
  currency?: string;
  pricing_model?: string;
  instance_count?: number;
  breakdown?: { [k: string]: number };
  cheapest?: boolean;
  assumptions?: string;
  selected_instance?: {
    sku?: string;
    type: string;
    vcpu: number;
    memory_gb: number;
    count?: number;
    price_per_month?: number;
    category?: string;
    description?: string;
  };
}

const colors: { [k: string]: string } = {
  aws: "from-amber-400 to-amber-600 text-gray-900",
  azure: "from-indigo-600 to-indigo-700 text-white",
  gcp: "from-rose-500 to-pink-600 text-white",
  kubernetes: "from-emerald-600 to-teal-600 text-white",
  onprem: "from-stone-200 to-stone-300 text-gray-900",
};

const ProviderCard: React.FC<Props> = ({ provider, total, currency, pricing_model, instance_count = 1, breakdown, cheapest, assumptions, selected_instance }) => {
  const [open, setOpen] = useState(false);
  const pricingLabel: Record<string, string> = {
    on_demand: 'On-Demand',
    reserved_1yr: '1-Yr Reserved — 38% off On-Demand',
    reserved_3yr: '3-Yr Reserved — 57% off On-Demand',
    spot: 'Spot — 70% off On-Demand',
    baseline: 'Baseline (TCO)',
    onprem_k8s: 'Baseline (TCO)',
  };
  const fmt = (v: number) => {
    try {
      if (!currency) return v.toString();
      return new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(v);
    } catch {
      return `${currency} ${v}`;
    }
  };
  if (!provider) return null;
  const p = provider.toLowerCase();
  const color = colors[p] || "from-gray-200 to-gray-400 text-gray-900";
  // Map provider to an accent color for the left stripe
  const accent: { [k: string]: string } = {
    aws: '#FF7A00',
    azure: '#0066CC',
    gcp: '#1A73E8',
    kubernetes: '#0EA5A3',
    onprem: '#9CA3AF',
  };

  const icons: { [k: string]: React.ReactNode } = {
    aws: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <path d="M3 7h18v4H3z" fill="currentColor" opacity="0.95"></path>
        <path d="M5 13h14v6H5z" fill="currentColor" opacity="0.7"></path>
      </svg>
    ),
    azure: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <path d="M12 2l7 12H5l7-12z" fill="currentColor" opacity="0.95" />
      </svg>
    ),
    gcp: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <circle cx="12" cy="12" r="10" fill="currentColor" opacity="0.95" />
      </svg>
    ),
    kubernetes: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <path d="M12 2l3 3-3 3-3-3 3-3z" fill="currentColor" opacity="0.95" />
        <circle cx="12" cy="12" r="2" fill="currentColor" opacity="0.7" />
      </svg>
    ),
    onprem: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
        <rect x="4" y="6" width="16" height="12" rx="2" fill="currentColor" opacity="0.95" />
      </svg>
    ),
  };
  const metricChips = (() => {
    if (!breakdown) return [] as Array<{ label: string; value: number | undefined }>;

    if (p === 'onprem') {
      return [
        { label: 'CapEx', value: breakdown.capex },
        { label: 'Power', value: breakdown.power },
        { label: 'Facilities', value: breakdown.facilities },
        { label: 'Operations', value: breakdown.operations },
        { label: 'Network', value: breakdown.network },
        { label: 'Backup', value: breakdown.backup },
      ];
    }

    if (p === 'kubernetes') {
      return [
        { label: 'CapEx', value: breakdown.capex },
        { label: 'Power', value: breakdown.power },
        { label: 'Facilities', value: breakdown.facilities },
        { label: 'Operations', value: breakdown.operations },
        { label: 'K8s Overhead', value: breakdown.k8s_overhead },
        { label: 'Network', value: breakdown.network },
        { label: 'Backup', value: breakdown.backup },
      ];
    }

    return [
      { label: 'Compute', value: breakdown.compute ?? breakdown.instance ?? breakdown.cpu },
      { label: 'Storage', value: breakdown.storage },
      { label: 'Network', value: breakdown.network },
      { label: 'Backup', value: breakdown.backup },
    ];
  })();

  try {
    return (
      <div data-testid={`card-${p}`} className={`plan-tile ${cheapest ? 'cheapest pulse' : ''} card-accent-left text-slate-800`} style={{boxShadow: '0 6px 28px rgba(2,6,23,0.06)'}}>
        <div className="plan-header">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-md bg-white/10 flex items-center justify-center">
              <picture>
                <source srcSet={`/assets/${p}.svg`} type="image/svg+xml" />
                <img src={`/assets/${p}.svg`} alt={`${provider} logo`} className="provider-img object-contain relative z-10" />
              </picture>
            </div>
            <div>
              <div className="plan-name">{provider}</div>
              {pricing_model ? <div className="inline-flex mt-1 text-[11px] px-2 py-0.5 rounded-full border border-cyan-400/40 bg-cyan-400/10 text-cyan-300">{pricingLabel[pricing_model] || pricing_model}</div> : null}
              {selected_instance ? (
                <div className="text-xs text-slate-600 font-mono">
                  {p === 'kubernetes' || p === 'onprem'
                    ? `${selected_instance.type || 'Workload baseline'} • ${selected_instance.vcpu} vCPU • ${selected_instance.memory_gb} GB RAM`
                    : `${(selected_instance.sku || selected_instance.type)} • ${selected_instance.vcpu} vCPU • ${selected_instance.memory_gb} GB RAM`}
                </div>
              ) : (
                <div className="price-sub">per month • estimated</div>
              )}
              {instance_count > 1 ? <div className="text-xs text-slate-600">Instance Count: {instance_count}</div> : null}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {cheapest && p !== 'onprem' ? <div className="provider-chip cheapest" aria-hidden><span className="dot" style={{background: accent[p]}} />Cheapest</div> : null}
            <button 
              onClick={() => setOpen(!open)} 
              className="text-sm text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 px-3 py-1 rounded transition-colors"
            >
              {open ? 'Hide' : 'Details'}
            </button>
          </div>
        </div>

        <div className="mt-3 flex items-end justify-between">
          <div>
            <div className="price-large">{currency ? new Intl.NumberFormat(undefined, {style:'currency', currency}).format(Number(total)) : String(total)}</div>
            {instance_count > 1 && selected_instance?.price_per_month ? (
              <div className="text-sm text-gray-500 mt-1">
                {fmt(Number(selected_instance.price_per_month))}/instance × {instance_count} = {fmt(Number(total))}/month
              </div>
            ) : (
              <div className="text-sm text-gray-500 mt-1">Estimated monthly cost</div>
            )}
          </div>
          <div className="w-20 h-20 rounded-md overflow-hidden relative flex items-center justify-center">
            <img src={`/assets/${p}.svg`} alt={`${provider} logo`} className="provider-img object-contain" />
          </div>
        </div>

        <div className="mt-4 flex gap-2 flex-wrap">
          {metricChips.map(({ label, value }) => {
            if (value === undefined) return null;
            return (
              <div key={label} className="stat-chip">
                <div className="stat-key">{label}</div>
                <div className="stat-val">{fmt(Number(value))}</div>
              </div>
            );
          })}
        </div>

        <div className={`overflow-hidden transition-[max-height] duration-200 ${open ? 'max-h-96 p-3 bg-slate-50' : 'max-h-0 p-0 bg-transparent'}`}>
          {breakdown ? (
            <div className="space-y-2">
              <ul className="text-sm text-slate-700 space-y-1">
                {Object.entries(breakdown).map(([k, v]) => (
                  <li key={k} className="flex justify-between">
                    <span className="capitalize">{k}</span>
                    <span className="font-mono">{fmt(Number(v))}</span>
                  </li>
                ))}
              </ul>
              {assumptions ? (
                <div className="text-[11px] leading-snug text-slate-500 italic">
                  {assumptions}
                </div>
              ) : null}
            </div>
          ) : (
            <div className="text-sm text-slate-600">No details available</div>
          )}
        </div>

      </div>
    );
  } catch (err) {
    // Log and fail gracefully to avoid breaking other cards
    // eslint-disable-next-line no-console
    console.error('ProviderCard render error', err);
    return (
      <div data-testid={`card-error`} className="rounded-lg p-4 border bg-red-50 text-red-700">Error rendering {provider}</div>
    );
  }
};

export default ProviderCard;
