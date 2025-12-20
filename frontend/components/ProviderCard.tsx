"use client";
import React, { useState } from "react";

interface Props {
  provider: string;
  total: number | string;
  currency?: string;
  breakdown?: { [k: string]: number };
  cheapest?: boolean;
  imageMode?: 'illustration' | 'photo';
}

const colors: { [k: string]: string } = {
  aws: "from-amber-400 to-amber-600 text-gray-900",
  azure: "from-indigo-600 to-indigo-700 text-white",
  gcp: "from-rose-500 to-pink-600 text-white",
  kubernetes: "from-emerald-600 to-teal-600 text-white",
  onprem: "from-stone-200 to-stone-300 text-gray-900",
};

const ProviderCard: React.FC<Props> = ({ provider, total, currency, breakdown, cheapest, imageMode = 'illustration' }) => {
  const [open, setOpen] = useState(false);
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

  try {
    return (
    <div data-testid={`card-${p}`} className={`rounded-lg overflow-hidden shadow-sm border dark:border-gray-600 card ${imageMode === 'photo' ? 'photo-mode' : ''} ${cheapest ? 'cheapest pulse' : ''} card-accent-left`} style={{boxShadow: '0 6px 24px rgba(2,6,23,0.06)'}}>
      <div style={{borderLeft: `6px solid ${accent[p] || '#ddd'}`}} className={`p-4 bg-gradient-to-br ${color} flex items-center justify-between gap-4`}>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white shadow-md flex items-center justify-center text-xl relative" style={{border: '1px solid rgba(255,255,255,0.18)'}}>
            {imageMode === 'photo' ? (
              <img
                src={`/assets/photos/photo_${p}.jpg`}
                alt=""
                aria-hidden
                className="photo-bg-img absolute inset-0 w-full h-full object-cover rounded-full opacity-90"
                onError={(e) => { (e.target as HTMLImageElement).src = `/assets/photo_${p}.svg`; }}
              />
            ) : null}
            <picture>
              <source srcSet={`/assets/${p}.svg`} type="image/svg+xml" />
              <img src={`/assets/${p}.svg`} alt={`${provider} logo`} className="provider-img object-contain relative z-10" />
            </picture>
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-medium uppercase opacity-90">{provider}</div>
                <div className="price-meta">per month • estimated</div>
              </div>
              {cheapest ? <div className="provider-chip" aria-hidden><span className="dot" style={{background: accent[p]}} />Cheapest</div> : null}
            </div>

            <div className="mt-3 flex items-end gap-4">
              <div className="flex-1">
                <div className="price-large">{currency ? new Intl.NumberFormat(undefined, {style:'currency', currency}).format(Number(total)) : String(total)}</div>
                <div className="text-sm text-gray-500 mt-1">Estimated monthly cost</div>
              </div>
              <div className="text-right">
                <button className="px-3 py-1 rounded bg-white/10 hover:bg-white/20">Details</button>
              </div>
            </div>

            <div className="mt-4 flex gap-2 flex-wrap">
              {['cpu','ram','storage','network'].map((k) => (
                breakdown && breakdown[k] !== undefined ? (
                  <div key={k} className="stat-chip">
                    <div className="stat-key">{k.toUpperCase()}</div>
                    <div className="stat-val">{k === 'ram' ? `${Number(breakdown[k])} GB` : k === 'storage' ? `${Number(breakdown[k])} GB` : k === 'network' ? `${Number(breakdown[k])} Mbps` : `${Number(breakdown[k])}`}</div>
                  </div>
                ) : null
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            className="text-sm bg-white/10 hover:bg-white/20 px-3 py-1 rounded transition"
            onClick={() => setOpen(!open)}
            aria-expanded={open}
          >
            {open ? "Hide" : "Details"}
          </button>
        </div>
      </div>
      <div className={`p-4 bg-gray-50 dark:bg-gray-800 overflow-hidden transition-[max-height] duration-200 ${open ? 'max-h-96' : 'max-h-0'}`}>
        {breakdown ? (
          <ul className="text-sm text-gray-700 dark:text-gray-200 space-y-1">
            {Object.entries(breakdown).map(([k, v]) => (
              <li key={k} className="flex justify-between">
                <span className="capitalize">{k}</span>
                <span className="font-mono">{fmt(Number(v))}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-sm text-gray-600 dark:text-gray-300">No details available</div>
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
