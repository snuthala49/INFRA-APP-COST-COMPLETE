"use client";
import React from 'react';

interface SelectedInstance {
  sku?: string;
  family?: string;
  vcpu?: number;
  ram_gb?: number;
  count?: number;
  price_per_hour?: number;
  price_per_month?: number;
}

interface Result {
  provider: string;
  total: number;
  currency?: string;
  breakdown?: { [k: string]: number };
  selected_instance?: SelectedInstance;
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
                <th key={r.provider} className="pr-6">{r.provider}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row} className="border-t">
                <td className="py-3 text-sm font-medium">{row}</td>
                {results.map((r) => {
                  let cellValue: string | React.ReactNode = '-';
                  
                  if (row === 'Monthly') {
                    cellValue = (
                      <span className="font-semibold">
                        {new Intl.NumberFormat(undefined, {style:'currency', currency: r.currency || 'USD'}).format(r.total * multiplier)}
                      </span>
                    );
                  } else if (row === 'CPU' && r.selected_instance) {
                    cellValue = <span className="text-gray-600">{r.selected_instance.vcpu}</span>;
                  } else if (row === 'RAM' && r.selected_instance) {
                    cellValue = <span className="text-gray-600">{r.selected_instance.ram_gb} GB</span>;
                  } else if (r.breakdown && r.breakdown[row.toLowerCase()] !== undefined) {
                    cellValue = <span className="text-gray-600">${r.breakdown[row.toLowerCase()].toFixed(2)}</span>;
                  }
                  
                  return (
                    <td key={r.provider + row} className="py-3 text-sm">
                      {cellValue}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PricingTable;
