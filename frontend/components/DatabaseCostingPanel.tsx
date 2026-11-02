"use client";

import React, { useMemo, useState } from "react";

type DatabaseProvider = "aws" | "azure" | "gcp";

interface DatabaseRate {
  rate_id: string;
  component: string;
  sku: string;
  unit?: string;
  unit_price: number;
  currency: string;
  source: string;
  effective_date: string | null;
}

interface DatabaseCatalog {
  rates: DatabaseRate[];
  rate_count?: number;
  region_rate_count?: number;
  truncated?: boolean;
  provider_status?: { status?: string; updated_at?: string | null };
  updated_at?: string | null;
}

interface QuoteLine {
  key: number;
  rateId: string;
  quantity: number;
}

interface QuoteResult {
  provider: string;
  service: string;
  region: string;
  currency: string;
  total: number;
  line_items: Array<{
    rate_id: string;
    component: string;
    sku: string;
    price_region_scope?: string;
    quantity: number;
    unit?: string;
    unit_price: number;
    subtotal: number;
    source: string;
    effective_date: string | null;
  }>;
  price_status?: { status?: string; updated_at?: string | null };
  prices_updated_at?: string | null;
}

const services: Record<DatabaseProvider, Array<{ key: string; label: string }>> = {
  aws: [
    { key: "rds", label: "Amazon RDS" },
    { key: "aurora", label: "Amazon Aurora" },
    { key: "dynamodb", label: "DynamoDB" },
    { key: "redshift", label: "Redshift" },
  ],
  azure: [
    { key: "azure_sql", label: "Azure SQL Database" },
    { key: "azure_sql_managed_instance", label: "Azure SQL Managed Instance" },
    { key: "azure_postgresql", label: "Azure Database for PostgreSQL" },
    { key: "cosmos_db", label: "Cosmos DB" },
    { key: "synapse", label: "Synapse Analytics" },
  ],
  gcp: [
    { key: "cloud_sql", label: "Cloud SQL" },
    { key: "spanner", label: "Spanner" },
    { key: "firestore", label: "Firestore" },
    { key: "bigtable", label: "Bigtable" },
    { key: "bigquery", label: "BigQuery" },
  ],
};

const defaultRegions: Record<DatabaseProvider, string> = {
  aws: "us-east-1",
  azure: "eastus",
  gcp: "us-central1",
};

const formatCurrency = (value: number, currency = "USD") =>
  new Intl.NumberFormat(undefined, { style: "currency", currency }).format(value);

export default function DatabaseCostingPanel({ apiBase }: { apiBase: string }) {
  const [provider, setProvider] = useState<DatabaseProvider>("aws");
  const [service, setService] = useState("rds");
  const [region, setRegion] = useState(defaultRegions.aws);
  const [componentFilter, setComponentFilter] = useState("all");
  const [rateSearch, setRateSearch] = useState("");
  const [catalog, setCatalog] = useState<DatabaseCatalog | null>(null);
  const [lines, setLines] = useState<QuoteLine[]>([]);
  const [result, setResult] = useState<QuoteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const selectedRates = useMemo(() => new Map((catalog?.rates || []).map((rate) => [rate.rate_id, rate])), [catalog]);

  const changeProvider = (nextProvider: DatabaseProvider) => {
    setProvider(nextProvider);
    setService(services[nextProvider][0].key);
    setRegion(defaultRegions[nextProvider]);
    setCatalog(null);
    setLines([]);
    setResult(null);
    setError(null);
  };

  const loadPrices = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setLines([]);
    try {
      const params = new URLSearchParams({ provider, service, region: region.trim() });
      params.set("component", componentFilter);
      if (rateSearch.trim()) params.set("search", rateSearch.trim());
      const response = await fetch(`${apiBase}/api/database/catalog?${params}`);
      const data = await response.json();
      const providerStatus = data.provider_status || data.providers?.[provider];
      if (!response.ok) throw new Error(providerStatus?.error || data.error || "Unable to load database prices");
      setCatalog(data);
      if (!data.rates?.length) {
        throw new Error(providerStatus?.error || `No cached ${provider} ${service} rates for ${region}. Sync the database price catalog first.`);
      }
    } catch (loadError) {
      setCatalog(null);
      setError(loadError instanceof Error ? loadError.message : "Unable to load database prices");
    } finally {
      setLoading(false);
    }
  };

  const addLine = () => {
    const firstRate = catalog?.rates[0];
    if (!firstRate) return;
    setLines((current) => [...current, { key: Date.now() + current.length, rateId: firstRate.rate_id, quantity: 1 }]);
  };

  const calculate = async () => {
    if (!lines.length) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/api/database/calculate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider,
          service,
          region: region.trim(),
          line_items: lines.map(({ rateId, quantity }) => ({ rate_id: rateId, quantity })),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to calculate database estimate");
      setResult(data);
    } catch (calculateError) {
      setError(calculateError instanceof Error ? calculateError.message : "Unable to calculate database estimate");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="max-w-6xl mx-auto px-4 py-8" aria-labelledby="database-estimate-heading">
      <div className="rounded-lg border border-slate-700 bg-slate-900/70 p-5 md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 id="database-estimate-heading" className="text-xl font-semibold text-slate-100">Database estimate</h2>
            <p className="mt-1 text-sm text-slate-300">Build a monthly estimate from the provider’s published price units.</p>
          </div>
          {catalog?.provider_status?.status ? (
            <span className="rounded border border-slate-600 px-2 py-1 text-xs text-slate-200">Prices: {catalog.provider_status.status}</span>
          ) : null}
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <label className="text-sm text-slate-200">
            Provider
            <select value={provider} onChange={(event) => changeProvider(event.target.value as DatabaseProvider)} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100">
              <option value="aws">AWS</option>
              <option value="azure">Azure</option>
              <option value="gcp">Google Cloud</option>
            </select>
          </label>
          <label className="text-sm text-slate-200">
            Database service
            <select value={service} onChange={(event) => { setService(event.target.value); setCatalog(null); setLines([]); setResult(null); }} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100">
              {services[provider].map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
            </select>
          </label>
          <label className="text-sm text-slate-200">
            Region
            <input value={region} onChange={(event) => { setRegion(event.target.value); setCatalog(null); setLines([]); setResult(null); }} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100" />
          </label>
          <label className="text-sm text-slate-200">
            Price component
            <select value={componentFilter} onChange={(event) => { setComponentFilter(event.target.value); setCatalog(null); setLines([]); setResult(null); }} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100">
              <option value="all">All components</option>
              <option value="compute">Compute</option>
              <option value="memory">Memory</option>
              <option value="storage">Storage</option>
              <option value="backup">Backup</option>
              <option value="iops">IOPS</option>
              <option value="read">Read operations</option>
              <option value="write">Write operations</option>
              <option value="operations">Other operations</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="text-sm text-slate-200">
            Filter SKU or meter
            <input value={rateSearch} onChange={(event) => { setRateSearch(event.target.value); setCatalog(null); setLines([]); setResult(null); }} placeholder="e.g. db.t3.medium, gp3" className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100" />
          </label>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button type="button" onClick={loadPrices} disabled={loading || !region.trim()} className="rounded bg-cyan-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{loading ? "Loading..." : "Load prices"}</button>
          {catalog?.rates.length ? <button type="button" onClick={addLine} className="rounded border border-slate-500 px-4 py-2 text-sm text-slate-100">Add cost line</button> : null}
        </div>

        {catalog?.rates.length ? (
          <>
            <div className="mt-3 text-xs text-slate-400">Showing {catalog.rates.length} of {catalog.rate_count ?? catalog.rates.length} matching rates ({catalog.region_rate_count ?? catalog.rates.length} for this service and region). Cache refreshed: {catalog.updated_at || "unknown"}. Enter quantities in each selected API unit.</div>
            <div className="mt-3 space-y-3">
              {lines.map((line, index) => {
                const selectedRate = selectedRates.get(line.rateId);
                return (
                  <div key={line.key} className="grid grid-cols-1 items-end gap-3 border-t border-slate-700 pt-3 sm:grid-cols-[minmax(0,1fr)_12rem_auto]">
                    <label className="text-sm text-slate-200">
                      Price line
                      <select value={line.rateId} onChange={(event) => setLines((current) => current.map((item) => item.key === line.key ? { ...item, rateId: event.target.value } : item))} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100">
                        {catalog.rates.map((rate) => <option key={rate.rate_id} value={rate.rate_id}>{rate.component} · {rate.sku} · {formatCurrency(rate.unit_price, rate.currency)}/{rate.unit || "unit"}</option>)}
                      </select>
                    </label>
                    <label className="text-sm text-slate-200">
                      Quantity ({selectedRate?.unit || "unit"})
                      <input type="number" min="0" step="any" value={line.quantity} aria-label={`Quantity for database line ${index + 1}`} onChange={(event) => setLines((current) => current.map((item) => item.key === line.key ? { ...item, quantity: Number(event.target.value) } : item))} className="mt-1 w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-100" />
                    </label>
                    <button type="button" aria-label={`Remove database line ${index + 1}`} onClick={() => setLines((current) => current.filter((item) => item.key !== line.key))} className="rounded border border-slate-600 px-3 py-2 text-sm text-slate-200">Remove</button>
                  </div>
                );
              })}
            </div>
            {lines.length ? <button type="button" onClick={calculate} disabled={loading} className="mt-4 rounded bg-emerald-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">Calculate database cost</button> : null}
          </>
        ) : null}

        {error ? <p role="alert" className="mt-3 text-sm text-rose-300">{error}</p> : null}
        {result ? (
          <div className="mt-5 border-t border-slate-700 pt-4" data-testid="database-estimate-result">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-base font-semibold text-slate-100">{result.provider.toUpperCase()} {result.service} · {result.region}</h3>
              <span className="text-xl font-bold text-emerald-300">{formatCurrency(result.total, result.currency)}/month</span>
            </div>
            <ul className="mt-3 divide-y divide-slate-700 text-sm">
              {result.line_items.map((line) => <li key={line.rate_id} className="flex flex-wrap justify-between gap-2 py-2 text-slate-200"><span>{line.component} · {line.sku} · {line.quantity} {line.unit}{line.price_region_scope ? ` · price scope ${line.price_region_scope}` : ""}</span><span>{formatCurrency(line.subtotal, result.currency)}</span></li>)}
            </ul>
            <p className="mt-2 text-xs text-slate-400">Rates from provider price catalogs; effective date is shown per line. Estimate includes only the selected lines.</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}