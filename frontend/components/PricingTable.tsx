"use client";
import React from 'react';

interface Result {
  provider: string;
  total: number;
  currency?: string;
  breakdown?: { [k: string]: number };
  selected_instance?: {
    type?: string;
    vcpu: number;
    memory_gb: number;
    category?: string;
    description?: string;
  };
  assumptions?: string;
}

interface Props { results: Result[]; multiplier?: number; period?: 'monthly' | 'annual' }

const PricingTable: React.FC<Props> = ({ results, multiplier = 1, period = 'monthly' }) => {
  const costLabel = period === 'annual' ? 'Annual' : 'Monthly';
  const rows = [
    'Instance', 'vCPU', 'RAM (GB)', 'Compute / CapEx', 'Storage', 'Power',
    'Facilities', 'Operations', 'Maintenance', 'Software licensing',
    'K8s overhead', 'Network ingress', 'Network egress', 'Backup', costLabel,
  ];

  const formatCurrency = (value: number, currency = 'USD') =>
    new Intl.NumberFormat(undefined, { style: 'currency', currency }).format(value);

  const rowDisplayValue = (row: string, r: Result) => {
    const p = r.provider.toLowerCase();
    
    if (row === 'Instance') {
      if (p === 'kubernetes') return 'K8s cluster baseline';
      if (p === 'onprem') return 'On-prem hardware baseline';
      return r.selected_instance?.type || '-';
    }
    
    if (row === 'vCPU') {
      return r.selected_instance?.vcpu ?? '-';
    }
    
    if (row === 'RAM (GB)') {
      return r.selected_instance?.memory_gb ?? '-';
    }
    
    const breakdown = r.breakdown || {};
    const breakdownKey: Record<string, string> = {
      'Compute / CapEx': breakdown.instance !== undefined ? 'instance' : 'capex',
      'Storage': 'storage',
      'Power': 'power',
      'Facilities': 'facilities',
      'Operations': 'operations',
      'Maintenance': 'maintenance',
      'Software licensing': 'software_licensing',
      'K8s overhead': 'k8s_overhead',
      'Network ingress': 'network_ingress',
      'Network egress': 'network_egress',
      'Backup': 'backup',
    };
    const key = breakdownKey[row];
    if (row === 'Storage' && breakdown.storage === undefined && ['onprem', 'kubernetes'].includes(p)) {
      return 'Included in infrastructure baseline';
    }
    if (key && breakdown[key] !== undefined) return formatCurrency(breakdown[key], r.currency || 'USD');
    if (key && ['Network ingress', 'Power', 'Facilities', 'Operations', 'Maintenance', 'Software licensing', 'K8s overhead'].includes(row)) {
      return formatCurrency(0, r.currency || 'USD');
    }
    return '-';
  };

  return (
    <div className="card p-4 mt-6">
      <h4 className="text-base font-bold text-slate-800 mb-3">Comparison</h4>
      <div className="overflow-x-auto">
        <table className="w-full table-auto pricing-table">
          <thead>
            <tr className="text-left text-sm text-slate-600">
              <th className="pr-6 font-semibold text-slate-700">Feature</th>
              {results.map((r) => (
                <th key={r.provider} className="pr-6 font-semibold text-slate-700">
                  {r.provider}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row} className="border-t">
                <td className="py-3 text-sm font-semibold text-slate-700">{row}</td>
                {results.map((r) => (
                  <td key={r.provider + row} className="py-3 text-sm">
                    {row === costLabel ? (
                      <span className="font-bold text-slate-900">{formatCurrency(r.total * multiplier, r.currency || 'USD')}</span>
                    ) : (
                      <span className="text-slate-600">{rowDisplayValue(row, r)}</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Assumptions section below table */}
      <div className="mt-4 space-y-2">
        {results.map((r, idx) => r.assumptions ? (
          <details key={idx} className="text-xs text-slate-500">
            <summary className="cursor-pointer font-semibold text-slate-600 hover:text-slate-800">
              {r.provider} assumptions
            </summary>
            <p className="mt-1 pl-4 italic leading-snug text-slate-500">{r.assumptions}</p>
          </details>
        ) : null)}
      </div>
    </div>
  );
};

export default PricingTable;
