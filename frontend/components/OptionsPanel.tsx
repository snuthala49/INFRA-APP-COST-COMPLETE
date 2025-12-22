"use client";
import React from 'react';
import InputField from './InputField';

interface OptionsPanelProps {
  cpu: number;
  ram: number;
  storage: number;
  network: number;
  backup: number;
  setCpu: (value: number) => void;
  setRam: (value: number) => void;
  setStorage: (value: number) => void;
  setNetwork: (value: number) => void;
  setBackup: (value: number) => void;
  period: 'monthly' | '6mo' | 'annual';
  setPeriod: (value: 'monthly' | '6mo' | 'annual') => void;
  onCalculate: () => void;
  loading: boolean;
}

const OptionsPanel: React.FC<OptionsPanelProps> = ({
  cpu,
  ram,
  storage,
  network,
  backup,
  setCpu,
  setRam,
  setStorage,
  setNetwork,
  setBackup,
  period,
  setPeriod,
  onCalculate,
  loading,
}) => {
  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold mb-4">Configure</h3>

      <div className="space-y-4 mb-6">
        <InputField
          label="CPU Cores"
          value={cpu}
          onChange={setCpu}
          min={1}
          max={128}
        />
        <InputField
          label="RAM (GB)"
          value={ram}
          onChange={setRam}
          min={1}
          max={1024}
        />
        <InputField
          label="Storage (GB)"
          value={storage}
          onChange={setStorage}
          min={0}
          max={100000}
        />
        <InputField
          label="Network (Mbps)"
          value={network}
          onChange={setNetwork}
          min={0}
          max={100000}
        />
        <InputField
          label="Backup (GB)"
          value={backup}
          onChange={setBackup}
          min={0}
          max={100000}
        />
      </div>

      <div className="mb-6">
        <label className="text-sm font-medium block mb-3">Billing Period</label>
        <div className="flex gap-2">
          {(['monthly', '6mo', 'annual'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all ${
                period === p
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {p === 'monthly' ? 'Monthly' : p === '6mo' ? '6 Months' : 'Annual'}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={onCalculate}
        disabled={loading}
        className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-cyan-500 text-white rounded-lg font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {loading ? 'Calculating...' : 'Calculate'}
      </button>
    </div>
  );
};

export default OptionsPanel;
