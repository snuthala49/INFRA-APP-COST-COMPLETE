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
  period: string;
  setPeriod: (p: string) => void;
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
        <div className="text-sm text-gray-500 mb-2">Billing period</div>
        <div className="flex gap-2">
          <button onClick={() => setPeriod('monthly')} className={`px-3 py-1 rounded ${period === 'monthly' ? 'bg-indigo-600 text-white' : 'bg-white/6'}`}>Monthly</button>
          <button onClick={() => setPeriod('6mo')} className={`px-3 py-1 rounded ${period === '6mo' ? 'bg-indigo-600 text-white' : 'bg-white/6'}`}>6 months</button>
          <button onClick={() => setPeriod('annual')} className={`px-3 py-1 rounded ${period === 'annual' ? 'bg-indigo-600 text-white' : 'bg-white/6'}`}>Annual</button>
        </div>
      </div>

      <button data-testid="calculate-btn" onClick={onCalculate} disabled={loading} className="mt-6 w-full btn-primary py-3 text-lg">
        {loading ? 'Calculating...' : 'Show prices'}
      </button>
    </div>
  );
};

export default OptionsPanel;
