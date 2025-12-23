"use client";
import React from 'react';
import InputField from './InputField';

interface Props {
  cpu: number;
  ram: number;
  storage: number;
  network: number;
  backup: number;
  setCpu: (n: number) => void;
  setRam: (n: number) => void;
  setStorage: (n: number) => void;
  setNetwork: (n: number) => void;
  setBackup: (n: number) => void;
  period: 'monthly' | 'annual';
  setPeriod: (p: 'monthly' | 'annual') => void;
  onCalculate: () => void;
  loading: boolean;
}

const OptionsPanel: React.FC<Props> = ({ cpu, ram, storage, network, backup, setCpu, setRam, setStorage, setNetwork, setBackup, period, setPeriod, onCalculate, loading }) => {
  return (
    <div className="calculator-panel card">
      <h3 className="text-lg font-semibold mb-3">Configure instance</h3>
      <div className="grid gap-3">
        <InputField label="CPU (vCPUs)" value={cpu} onChange={setCpu} />
        <InputField label="RAM (GB)" value={ram} onChange={setRam} />
        <InputField label="Storage (GB)" value={storage} onChange={setStorage} />
        <InputField label="Network (Mbps)" value={network} onChange={setNetwork} />
        <InputField label="Backup (GB)" value={backup} onChange={setBackup} />
      </div>

      <div className="mt-4">
        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Billing period</div>
        <div className="flex gap-2">
          <button 
            onClick={() => setPeriod('monthly')} 
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
              period === 'monthly' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            Monthly
          </button>
          <button 
            onClick={() => setPeriod('annual')} 
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
              period === 'annual' 
                ? 'bg-indigo-600 text-white' 
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            Annual <span className="text-xs opacity-75">(15% off)</span>
          </button>
        </div>
      </div>

      <button data-testid="calculate-btn" onClick={onCalculate} disabled={loading} className="mt-6 w-full btn-primary py-3 text-lg">
        {loading ? 'Calculating...' : 'Show prices'}
      </button>
    </div>
  );
};

export default OptionsPanel;
