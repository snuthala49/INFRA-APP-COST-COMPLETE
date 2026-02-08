"use client";
import React from 'react';

interface Result {
  provider: string;
  total: number;
  currency?: string;
  breakdown?: { [k: string]: number };
  selected_instance?: {
    vcpu: number;
    memory_gb: number;
  };
  assumptions?: string;
}

interface Props { results: Result[]; multiplier?: number }

const PricingTable: React.FC<Props> = ({ results, multiplier = 1 }) => {
  const rows = ['CPU','RAM','Storage','Network','Backup','Monthly','Assumptions'];
  const getRowValue = (row: string, r: Result) => {
    if (row === 'CPU') {
      return r.breakdown?.compute ?? r.breakdown?.cpu;
    }
    if (row === 'RAM') {
      return r.breakdown?.compute ?? r.breakdown?.ram;
    }
    if (row === 'Storage') {
      return r.breakdown?.storage;
    }
    if (row === 'Network') {
      return r.breakdown?.network;
    }
    if (row === 'Backup') {
      return r.breakdown?.backup;
    }
    const key = row.toLowerCase();
    return r.breakdown?.[key];
  };

  return (
    <div className="card p-4 mt-6">
      <h4 className="text-sm text-gray-600 mb-3">Comparison</h4>
      <div className="overflow-x-auto">
        <table className="w-full table-auto pricing-table">
          <thead>
            <tr className="text-left text-sm text-gray-500">
              <th className="pr-6">Feature</th>
              {results.map((r) => (
                <th key={r.provider} className="pr-6 font-semibold text-gray-700 dark:text-gray-300">
                  {r.provider}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row} className="border-t">
                <td className="py-3 text-sm font-medium">{row}</td>
                {results.map((r) => (
                  <td key={r.provider + row} className="py-3 text-sm">
                    {row === 'Monthly' ? (
                      <span className="font-semibold">{new Intl.NumberFormat(undefined, {style:'currency', currency: r.currency || 'USD'}).format(r.total * multiplier)}</span>
                    ) : row === 'Assumptions' ? (
                      <span className="text-gray-500 text-xs leading-snug">{r.assumptions || '-'}</span>
                    ) : (
                      <span className="text-gray-600">{getRowValue(row, r) !== undefined ? new Intl.NumberFormat(undefined, {style:'currency', currency: r.currency || 'USD'}).format(Number(getRowValue(row, r))) : '-'}</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PricingTable;
