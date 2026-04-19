"use client";

import React, { useEffect, useMemo, useState } from "react";
import InputField from "./InputField";
import InstanceSelector, { CatalogEntry } from "./InstanceSelector";
import StorageTypeSelector from "./StorageTypeSelector";

export type ProviderKey = "aws" | "azure" | "gcp";

interface CatalogPayload {
  aws: CatalogEntry[];
  azure: CatalogEntry[];
  gcp: CatalogEntry[];
  storage_rates: {
    aws: Record<string, number>;
    azure: Record<string, number>;
    gcp: Record<string, number>;
  };
}

interface Props {
  apiBase: string;
  storage: number;
  network: number;
  backup: number;
  instanceCount: number;
  pricingModel: "on_demand" | "reserved_1yr" | "reserved_3yr" | "spot";
  selectedSkus: Record<ProviderKey, string | null>;
  storageTypes: Record<ProviderKey, string>;
  setStorage: (n: number) => void;
  setNetwork: (n: number) => void;
  setBackup: (n: number) => void;
  setInstanceCount: (n: number) => void;
  setPricingModel: (p: "on_demand" | "reserved_1yr" | "reserved_3yr" | "spot") => void;
  setSelectedSkus: (value: Record<ProviderKey, string | null>) => void;
  setStorageTypes: (value: Record<ProviderKey, string>) => void;
  onWorkloadChange: (cpu: number, ram: number) => void;
  period: "monthly" | "annual";
  setPeriod: (p: "monthly" | "annual") => void;
  onCalculate: () => void;
  loading: boolean;
}

const fallbackCatalog: CatalogPayload = {
  aws: [
    {
      sku: "m6i.xlarge",
      family: "m6i",
      category: "general",
      vcpu: 4,
      ram_gb: 16,
      description: "General purpose",
      price_per_hour: { on_demand: 0.192, reserved_1yr: 0.119, reserved_3yr: 0.083, spot: 0.058 },
    },
  ],
  azure: [
    {
      sku: "Standard_D4s_v3",
      family: "D-series",
      category: "general",
      vcpu: 4,
      ram_gb: 16,
      description: "General purpose",
      price_per_hour: { on_demand: 0.2, reserved_1yr: 0.124, reserved_3yr: 0.086, spot: 0.06 },
    },
  ],
  gcp: [
    {
      sku: "n2-standard-4",
      family: "n2-standard",
      category: "general",
      vcpu: 4,
      ram_gb: 16,
      description: "General purpose",
      price_per_hour: { on_demand: 0.2, reserved_1yr: 0.124, reserved_3yr: 0.086, spot: 0.06 },
    },
  ],
  storage_rates: {
    aws: { gp3: 0.08, io2: 0.125, st1: 0.025, sc1: 0.015 },
    azure: { premium_ssd: 0.135, standard_ssd: 0.1, standard_hdd: 0.04, ultra_disk: 0.29 },
    gcp: { balanced_pd: 0.1, ssd_pd: 0.17, extreme_pd: 0.27, standard_pd: 0.04 },
  },
};

const pricingOptions = [
  { key: "on_demand", label: "On-Demand", savings: "" },
  { key: "reserved_1yr", label: "1-Yr Reserved", savings: "save 38%" },
  { key: "reserved_3yr", label: "3-Yr Reserved", savings: "save 57%" },
  { key: "spot", label: "Spot", savings: "save 70%" },
] as const;

const OptionsPanel: React.FC<Props> = ({
  apiBase,
  storage,
  network,
  backup,
  instanceCount,
  pricingModel,
  selectedSkus,
  storageTypes,
  setStorage,
  setNetwork,
  setBackup,
  setInstanceCount,
  setPricingModel,
  setSelectedSkus,
  setStorageTypes,
  onWorkloadChange,
  period,
  setPeriod,
  onCalculate,
  loading,
}) => {
  const [activeProvider, setActiveProvider] = useState<ProviderKey>("aws");
  const [catalogPayload, setCatalogPayload] = useState<CatalogPayload>(fallbackCatalog);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogWarning, setCatalogWarning] = useState(false);

  useEffect(() => {
    let mounted = true;
    const fetchCatalog = async () => {
      setCatalogLoading(true);
      try {
        const res = await fetch(`${apiBase}/catalog`);
        if (!res.ok) throw new Error("catalog fetch failed");
        const data = (await res.json()) as CatalogPayload;
        if (mounted) {
          setCatalogPayload(data);
          setCatalogWarning(false);
        }
      } catch {
        if (mounted) {
          setCatalogPayload(fallbackCatalog);
          setCatalogWarning(true);
        }
      } finally {
        if (mounted) setCatalogLoading(false);
      }
    };

    fetchCatalog();
    return () => {
      mounted = false;
    };
  }, [apiBase]);

  const activeCatalog = useMemo(() => catalogPayload[activeProvider], [catalogPayload, activeProvider]);

  useEffect(() => {
    const selectedSku = selectedSkus[activeProvider];
    if (!selectedSku) return;
    const entry = activeCatalog.find((item) => item.sku === selectedSku);
    if (entry) onWorkloadChange(entry.vcpu, entry.ram_gb);
  }, [activeProvider, activeCatalog, selectedSkus, onWorkloadChange]);

  return (
    <div className="calculator-panel card">
      <h3 className="text-lg font-semibold mb-3 text-slate-800">Configure instance</h3>

      <div className="mb-4 border-b border-slate-700">
        <div className="flex gap-3">
          {(["aws", "azure", "gcp"] as const).map((provider) => (
            <button
              key={provider}
              type="button"
              onClick={() => setActiveProvider(provider)}
              className={`pb-2 px-1 text-sm font-semibold uppercase tracking-wide border-b-2 ${
                activeProvider === provider
                  ? "text-cyan-300 border-cyan-400"
                  : "text-slate-400 border-transparent hover:text-slate-200"
              }`}
            >
              {provider}
            </button>
          ))}
        </div>
      </div>

      {catalogLoading ? (
        <div className="text-sm text-slate-300 mb-3">Loading catalog...</div>
      ) : null}

      {catalogWarning ? (
        <div className="mb-3 rounded-md border border-yellow-500/40 bg-yellow-500/10 text-yellow-300 text-xs px-3 py-2">
          Using cached catalog — prices may be stale
        </div>
      ) : null}

      <div className="space-y-3">
        <InstanceSelector
          provider={activeProvider}
          catalog={activeCatalog}
          selectedSku={selectedSkus[activeProvider]}
          onSkuChange={(sku) => setSelectedSkus({ ...selectedSkus, [activeProvider]: sku })}
          pricingModel={pricingModel}
        />

        <StorageTypeSelector
          provider={activeProvider}
          selectedType={storageTypes[activeProvider]}
          onTypeChange={(value) => setStorageTypes({ ...storageTypes, [activeProvider]: value })}
          storageRates={catalogPayload.storage_rates[activeProvider] || {}}
        />

        <InputField label="Storage (GB)" value={storage} onChange={setStorage} />
        <InputField label="Network (Mbps)" value={network} onChange={setNetwork} />
        <InputField label="Backup (GB)" value={backup} onChange={setBackup} />
        <InputField label="Instance Count" value={instanceCount} onChange={(value) => setInstanceCount(Math.max(1, Math.min(500, value)))} />
      </div>

      <div className="mt-4">
        <div className="text-sm text-slate-700 mb-2">Pricing model</div>
        <div className="grid grid-cols-2 gap-2">
          {pricingOptions.map((option) => (
            <button
              key={option.key}
              type="button"
              onClick={() => setPricingModel(option.key)}
              className={`rounded-md border px-2 py-2 text-xs text-left transition-colors ${
                pricingModel === option.key
                  ? "bg-cyan-500 text-white border-cyan-400"
                  : "bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600"
              }`}
            >
              <div>{option.label}</div>
              {option.savings ? <div className="text-[11px] opacity-85">{option.savings}</div> : null}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <div className="text-sm text-slate-700 mb-2">Billing period</div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setPeriod("monthly")}
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
              period === "monthly"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Monthly
          </button>
          <button
            type="button"
            onClick={() => setPeriod("annual")}
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
              period === "annual"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Annual <span className="text-xs opacity-75">(15% off)</span>
          </button>
        </div>
      </div>

      <button data-testid="calculate-btn" onClick={onCalculate} disabled={loading} className="mt-6 w-full btn-primary py-3 text-lg">
        {loading ? "Calculating..." : "Show prices"}
      </button>
    </div>
  );
};

export default OptionsPanel;
