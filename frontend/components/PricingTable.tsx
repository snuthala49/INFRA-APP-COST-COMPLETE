"use client";
import React from 'react';

interface Result {
  provider: string;
  total: number;
  currency?: string;
  breakdown?: { [k: string]: number };
}

interface Props { results: Result[]; multiplier?: number }

const PricingTable: React.FC<Props> = ({ results, multiplier = 1 }) => {
  const rows = ['CPU','RAM','Storage','Network','Backup','Monthly'];
  return (
    <div className="card p-4 mt-6">
      <h4 className="text-sm text-gray-600 mb-3">Comparison</h4>
      <div className="overflow-x-auto">
        <table className="w-full table-auto pricing-table">
          <thead>
            <tr className="text-left text-sm text-gray-500">
              <th className="pr-6">Feature</th>
              {results.map((r) => (
                <th key={r.provider} className="pr-6">
                  <div className="flex items-center justify-between gap-2">
                    <span>{r.provider}</span>
                    <button className="table-buy">Buy</button>
                  </div>
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
                    ) : (
                      <span className="text-gray-600">{r.breakdown && r.breakdown[row.toLowerCase()] !== undefined ? r.breakdown[row.toLowerCase()] : '-'}</span>
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
