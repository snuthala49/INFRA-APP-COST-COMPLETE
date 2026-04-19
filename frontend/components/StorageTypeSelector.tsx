"use client";

import React from "react";

interface StorageTypeSelectorProps {
  provider: "aws" | "azure" | "gcp";
  selectedType: string;
  onTypeChange: (value: string) => void;
  storageRates: Record<string, number>;
}

const StorageTypeSelector: React.FC<StorageTypeSelectorProps> = ({ provider, selectedType, onTypeChange, storageRates }) => {
  const options = Object.entries(storageRates);

  return (
    <div>
      <label className="block text-xs font-semibold text-slate-800 mb-1">Storage type</label>
      <select
        aria-label={`${provider.toUpperCase()} storage type`}
        value={selectedType}
        onChange={(e) => onTypeChange(e.target.value)}
        className="w-full px-3 py-2 rounded-md bg-slate-800 border border-slate-700 text-slate-100"
      >
        {options.map(([key, rate]) => (
          <option key={`${provider}-storage-${key}`} value={key}>
            {key} — ${rate.toFixed(3)}/GB/month
          </option>
        ))}
      </select>
    </div>
  );
};

export default StorageTypeSelector;
