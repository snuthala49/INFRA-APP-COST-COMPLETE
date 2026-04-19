"use client";

import React, { useMemo, useState } from "react";

export interface PricingModelRates {
  on_demand: number;
  reserved_1yr: number;
  reserved_3yr: number;
  spot: number;
}

export interface CatalogEntry {
  sku: string;
  family: string;
  category: "general" | "compute" | "memory" | "gpu" | "inference";
  vcpu: number;
  ram_gb: number;
  description?: string;
  price_per_hour: PricingModelRates;
}

interface InstanceSelectorProps {
  provider: "aws" | "azure" | "gcp";
  catalog: CatalogEntry[];
  selectedSku: string | null;
  onSkuChange: (sku: string | null) => void;
  pricingModel: string;
}

type FilterCategory = "all" | "general" | "compute" | "memory" | "gpu" | "inference";

const categoryPills: Array<{ key: FilterCategory; label: string }> = [
  { key: "all", label: "All" },
  { key: "general", label: "General Purpose" },
  { key: "compute", label: "Compute Optimized" },
  { key: "memory", label: "Memory Optimized" },
  { key: "gpu", label: "GPU" },
  { key: "inference", label: "Inference" },
];

const MONTHLY_HOURS = 730;

const modelToKey = (pricingModel: string): keyof PricingModelRates => {
  if (pricingModel === "reserved_1yr") return "reserved_1yr";
  if (pricingModel === "reserved_3yr") return "reserved_3yr";
  if (pricingModel === "spot") return "spot";
  return "on_demand";
};

const InstanceSelector: React.FC<InstanceSelectorProps> = ({ provider, catalog, selectedSku, onSkuChange, pricingModel }) => {
  const [category, setCategory] = useState<FilterCategory>("all");

  const selectedEntry = useMemo(() => catalog.find((entry) => entry.sku === selectedSku) || null, [catalog, selectedSku]);

  const families = useMemo(() => {
    const filtered = category === "all" ? catalog : catalog.filter((entry) => entry.category === category);
    return Array.from(new Set(filtered.map((entry) => entry.family))).sort();
  }, [catalog, category]);

  const [selectedFamily, setSelectedFamily] = useState<string>(selectedEntry?.family || "");

  const familyEntries = useMemo(() => {
    if (!selectedFamily) return [];
    const filteredByCategory = category === "all" ? catalog : catalog.filter((entry) => entry.category === category);
    return filteredByCategory.filter((entry) => entry.family === selectedFamily);
  }, [catalog, category, selectedFamily]);

  const priceKey = modelToKey(pricingModel);

  const monthlyPrice = selectedEntry ? selectedEntry.price_per_hour[priceKey] * MONTHLY_HOURS : 0;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {categoryPills.map((pill) => {
          const active = category === pill.key;
          return (
            <button
              key={`${provider}-${pill.key}`}
              type="button"
              onClick={() => setCategory(pill.key)}
              className={`px-2.5 py-1 rounded-full text-xs border transition-colors ${
                active
                  ? "border-cyan-400 bg-cyan-400/10 text-cyan-300"
                  : "border-slate-700 bg-slate-800 text-slate-300 hover:border-slate-600"
              }`}
            >
              {pill.label}
            </button>
          );
        })}
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-800 mb-1">Instance family</label>
        <select
          aria-label={`${provider.toUpperCase()} family`}
          value={selectedFamily}
          onChange={(e) => {
            const family = e.target.value;
            setSelectedFamily(family);
            onSkuChange(null);
          }}
          className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100"
        >
          <option value="">Auto-select (Smart Match)</option>
          {families.map((family) => (
            <option key={`${provider}-family-${family}`} value={family}>
              {family}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-800 mb-1">Specific SKU</label>
        <select
          aria-label={`${provider.toUpperCase()} SKU`}
          value={selectedSku || ""}
          onChange={(e) => onSkuChange(e.target.value || null)}
          className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100"
        >
          <option value="">Auto-select (Smart Match)</option>
          {familyEntries.map((entry) => (
            <option key={entry.sku} value={entry.sku}>
              {entry.sku} — {entry.vcpu} vCPU / {entry.ram_gb} GB — ${entry.price_per_hour[priceKey].toFixed(3)}/hr
            </option>
          ))}
        </select>
      </div>

      <div className="rounded-md border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs text-slate-200">
        {selectedEntry ? (
          <div className="flex flex-wrap gap-3">
            <span className="text-slate-100 font-medium">{selectedEntry.vcpu} vCPU</span>
            <span className="text-slate-100 font-medium">{selectedEntry.ram_gb} GB RAM</span>
            <span className="text-cyan-300 font-medium">${monthlyPrice.toFixed(2)}/month</span>
          </div>
        ) : (
          <span className="text-slate-200 italic">Smart matcher mode enabled for {provider.toUpperCase()}.</span>
        )}
      </div>
    </div>
  );
};

export default InstanceSelector;
